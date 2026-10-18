"""Build standard and WorkBuddy ZIPs from an explicit resource allowlist."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from skill_bundle import ROOT, NAME, bundle_files, file_bytes, manifest_version

def build(out, root=ROOT):
    root = Path(root).resolve(); out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    files = bundle_files(root); version = manifest_version(root); result = []
    for platform in ["standard", "workbuddy"]:
        target = out / (NAME + ("-workbuddy" if platform == "workbuddy" else "") + ".zip")
        hashes = {}
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                entry = NAME + "/" + path.relative_to(root).as_posix()
                data = file_bytes(path, root, platform); hashes[entry] = hashlib.sha256(data).hexdigest()
                info = zipfile.ZipInfo(entry, (2026, 10, 18, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        with zipfile.ZipFile(target) as archive:
            assert archive.testzip() is None and set(archive.namelist()) == set(hashes)
            for entry, sha in hashes.items():
                assert hashlib.sha256(archive.read(entry)).hexdigest() == sha
        result.append({"platform": platform, "file": target.name, "version": version,
                       "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "entries": hashes})
    (out / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "SHA256SUMS").write_text("".join(f"{x['sha256']}  {x['file']}\n" for x in result), encoding="utf-8")
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--out", default=str(ROOT / "dist")); a = p.parse_args()
    print(json.dumps(build(a.out), ensure_ascii=False))

if __name__ == "__main__":
    main()
