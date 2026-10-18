"""Shared, local-only packaging rules; no credentials or network access."""
from pathlib import Path
import re

NAME = "software-skill"
ROOT = Path(__file__).resolve().parent.parent
TOP_FILES = {"SKILL.md", "README.md", "NOTICE.md", "requirements.txt"}
TOP_DIRS = {"agents", "references", "scripts", "tests", "assets"}

def bundle_files(root=ROOT):
    root = Path(root).resolve()
    paths = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if not path.is_file() or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Bundle contains an external or symlinked resource")
        if (len(relative.parts) == 1 and relative.name in TOP_FILES) or relative.parts[0] in TOP_DIRS:
            paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(root).as_posix())

def manifest_version(root=ROOT):
    text = (Path(root) / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n") or not re.search(r"^name: software-skill$", text, re.M):
        raise ValueError("Unexpected skill manifest")
    match = re.search(r'^  version: "([0-9]+\.[0-9]+\.[0-9]+)"$', text, re.M)
    if not match:
        raise ValueError("Missing semantic version")
    return match.group(1)

def workbuddy_manifest(text, version):
    if not text.startswith("---\n"):
        raise ValueError("Missing frontmatter")
    extras = (
        'display_name: "软件开发与软著全流程"\n'
        'description_zh: "从选题、算法设计、开发验证到软著材料和审查修订"\n'
        'description_en: "Plan, implement, verify software and prepare Chinese software copyright materials."\n'
        f'version: "{version}"\n'
        'author: "software-skill"\n'
    )
    return "---\n" + extras + text[4:]

def file_bytes(path, root=ROOT, platform="standard"):
    if Path(path).relative_to(root).as_posix() == "SKILL.md" and platform == "workbuddy":
        return workbuddy_manifest(Path(path).read_text(encoding="utf-8"), manifest_version(root)).encode("utf-8")
    return Path(path).read_bytes()
