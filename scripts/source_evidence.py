#!/usr/bin/env python3
"""Freeze explicitly selected text sources; detect drift and compare mapped document lines.

Standard library only. Does not parse or write DOCX. Never changes project files.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_new(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def resolve_source(root, name):
    if not isinstance(name, str) or not name:
        raise ValueError("source path must be a nonempty relative string")
    name = name.replace("\\", "/")
    if Path(name).is_absolute() or PureWindowsPath(name).drive:
        raise ValueError("absolute source paths are not allowed")
    relative = Path(name)
    if ".." in relative.parts:
        raise ValueError("parent traversal is not allowed")
    target = (root / relative).resolve(strict=True)
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError("source must be a file inside the project")
    return target, relative.as_posix()


def physical_lines(text):
    # Only normalize platform newlines, not form feeds or other string contents.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text:
        return []
    parts = text.split("\n")
    return parts[:-1] if text.endswith("\n") else parts


def snapshot(project, selection, out, encoding="utf-8-sig", max_file_bytes=10485760):
    root = Path(project).resolve(strict=True)
    chosen = read_json(selection)
    if not isinstance(chosen, list) or not chosen:
        raise ValueError("selection must be a nonempty ordered JSON array of relative paths")
    seen = set()
    files = []
    for name in chosen:
        path, relative = resolve_source(root, name)
        if path in seen:
            raise ValueError("duplicate source selection")
        seen.add(path)
        if path.stat().st_size > max_file_bytes:
            raise ValueError("selected source exceeds the configured byte limit")
        data = path.read_bytes()
        content = data.decode(encoding, errors="strict")
        if "\x00" in content:
            raise ValueError("NUL-containing file is not supported as text source")
        lines = physical_lines(content)
        files.append({"path": relative, "sha256": digest(data), "bytes": len(data),
                      "physical_lines": len(lines),
                      "nonblank_lines": sum(bool(line.strip()) for line in lines),
                      "lines": lines})
    record = {"schema": 1, "created_at": datetime.now(timezone.utc).isoformat(),
              "project_root": str(root), "encoding": encoding,
              "scope": "selected-files-only", "files": files}
    write_new(out, record)
    return {"ok": True, "files": len(files),
            "physical_lines": sum(f["physical_lines"] for f in files),
            "nonblank_lines": sum(f["nonblank_lines"] for f in files),
            "snapshot_sha256": digest(Path(out).read_bytes())}


def check(manifest, project=None):
    record = read_json(manifest)
    if record.get("schema") != 1 or not record.get("files"):
        raise ValueError("unsupported or empty snapshot")
    root = Path(project or record["project_root"]).resolve(strict=True)
    issues, seen = [], set()
    for item in record["files"]:
        name = item["path"]
        try:
            path, relative = resolve_source(root, name)
            if path in seen:
                raise ValueError("duplicate source in snapshot")
            seen.add(path)
            data = path.read_bytes()
            if digest(data) != item["sha256"]:
                issues.append({"file": relative, "kind": "source_hash_changed"})
            actual = physical_lines(data.decode(record["encoding"], errors="strict"))
            if actual != item["lines"]:
                issues.append({"file": relative, "kind": "source_text_changed"})
            if len(item["lines"]) != item["physical_lines"]:
                issues.append({"file": relative, "kind": "invalid_line_count"})
        except (OSError, ValueError, UnicodeError) as error:
            issues.append({"file": name, "kind": type(error).__name__})
    return {"ok": not issues, "files": len(record["files"]), "issues": issues}


def compare(manifest, rendered, project=None):
    drift = check(manifest, project)
    if not drift["ok"]:
        return {"ok": False, "stage": "source-check", "issues": drift["issues"]}
    record, export = read_json(manifest), read_json(rendered)
    issues = []
    if export.get("snapshot_sha256") != digest(Path(manifest).read_bytes()):
        issues.append({"kind": "snapshot_binding_mismatch"})
    if export.get("scope") != "all-selected-source-lines":
        raise ValueError("compare requires all selected source lines, not front/back excerpts")
    doc = export.get("document", {})
    doc_path = Path(doc.get("path", ""))
    if not doc_path.is_absolute() or not doc_path.is_file():
        raise ValueError("document.path must name the actual absolute local document")
    if digest(doc_path.read_bytes()) != doc.get("sha256"):
        issues.append({"kind": "document_hash_changed"})
    tabsize = export.get("tab_expansion", 0)
    if type(tabsize) is not int or not 0 <= tabsize <= 16:
        raise ValueError("tab_expansion must be an integer from 0 to 16")
    expected = [(f["path"], i, line) for f in record["files"]
                for i, line in enumerate(f["lines"], 1)]
    rows = export.get("rows")
    if not isinstance(rows, list):
        raise ValueError("rows must be an ordered array")
    if len(expected) != len(rows):
        issues.append({"kind": "row_count_mismatch", "expected": len(expected), "actual": len(rows)})
    for index, (origin, row) in enumerate(zip(expected, rows), 1):
        file, line_no, source = origin
        if not isinstance(row, dict):
            raise ValueError("each mapped row must be an object")
        if (row.get("file"), row.get("line")) != (file, line_no):
            issues.append({"row": index, "kind": "source_order_or_line_mismatch"})
            continue
        segments = row.get("segments")
        if not isinstance(segments, list) or not segments or not all(isinstance(x, str) for x in segments):
            raise ValueError("segments must be a nonempty array of actual extracted strings")
        target = source.expandtabs(tabsize) if tabsize else source
        if "".join(segments) != target:
            issues.append({"file": file, "line": line_no, "kind": "content_mismatch"})
    return {"ok": not issues, "checked_lines": min(len(expected), len(rows)),
            "issues": issues, "limits": "Mapped text only; does not verify pagination, export provenance or legal compliance."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    freeze = commands.add_parser("snapshot")
    freeze.add_argument("--project", required=True)
    freeze.add_argument("--selection", required=True)
    freeze.add_argument("--out", required=True)
    freeze.add_argument("--encoding", default="utf-8-sig")
    freeze.add_argument("--max-file-bytes", type=int, default=10485760)
    for name in ("check", "compare"):
        child = commands.add_parser(name)
        child.add_argument("--manifest", required=True)
        child.add_argument("--project")
        child.add_argument("--report")
        if name == "compare":
            child.add_argument("--rendered", required=True)
    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            result = snapshot(args.project, args.selection, args.out, args.encoding, args.max_file_bytes)
        elif args.command == "check":
            result = check(args.manifest, args.project)
        else:
            result = compare(args.manifest, args.rendered, args.project)
        if getattr(args, "report", None):
            write_new(args.report, result)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["ok"] else 1
    except (OSError, ValueError, KeyError, TypeError, LookupError) as error:
        # No source contents or personal identifiers in diagnostics.
        print(json.dumps({"ok": False, "error": type(error).__name__,
                          "message": "Invalid input or unavailable file; inspect local paths, schema and encoding."}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
