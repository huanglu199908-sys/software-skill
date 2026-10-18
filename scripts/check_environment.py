"""Report local skill/runtime capabilities without installing or changing anything."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

def inspect(project=None, materials_dir=None):
    project = Path(project).resolve() if project else Path.cwd()
    roots = []
    if materials_dir:
        roots.append(Path(materials_dir).expanduser())
    for base in [project, Path.home()]:
        for folder in [".agents", ".codex", ".dsh", ".codebuddy"]:
            roots.append(base / folder / "skills/software-copyright-materials")
    material = next((p.resolve() for p in roots if (p / "SKILL.md").is_file()), None)
    office = shutil.which("officecli") or shutil.which("officecli.exe")
    version = None
    if office:
        try:
            result = subprocess.run([office, "--version"], capture_output=True, text=True,
                                    timeout=15, env={**os.environ, "OFFICECLI_SKIP_UPDATE": "1", "OFFICECLI_NO_AUTO_RESIDENT": "1"})
            version = result.stdout.strip() if result.returncode == 0 else "version check failed"
        except (OSError, subprocess.TimeoutExpired):
            version = "version check unavailable"
    return {"python_version": sys.version.split()[0], "python_supported": sys.version_info >= (3, 10),
            "project_directory_exists": project.is_dir(), "materials_skill": str(material) if material else None,
            "officecli": office, "officecli_version": version,
            "execution_policy": "Capabilities of the actual agent host must still be verified; no installations performed",
            "word_readiness": "Read the actual materials SKILL.md for required version and authorization"}

def main():
    p = argparse.ArgumentParser(description=__doc__);p.add_argument("--project");p.add_argument("--materials-dir");a=p.parse_args()
    print(json.dumps(inspect(a.project, a.materials_dir), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
