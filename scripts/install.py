"""Install exactly one local skill bundle, with explicit collision handling."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
from skill_bundle import ROOT, NAME, bundle_files, file_bytes, manifest_version

def destination(platform, scope, project=None, home=None, skills_dir=None):
    if skills_dir:
        return Path(skills_dir).expanduser().resolve() / NAME
    base = Path(home).expanduser().resolve() if home else Path.home()
    if scope == "project":
        if project is None:
            raise ValueError("--project is required for project scope")
        base = Path(project).expanduser().resolve(strict=True)
        if not base.is_dir():
            raise ValueError("Project must be a directory")
    folder = {"codex": ".agents", "agents": ".agents", "deepseek": ".dsh", "workbuddy": ".codebuddy"}[platform]
    return base / folder / "skills" / NAME

def install(platform, scope="user", project=None, home=None, skills_dir=None,
            replace=False, dry_run=False, source=ROOT):
    source = Path(source).resolve(strict=True)
    target = destination(platform, scope, project, home, skills_dir)
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError("Refusing a symlink or non-directory target")
    target = target.resolve()
    if source == target or source.is_relative_to(target) or target.is_relative_to(source):
        raise ValueError("Source and install target must not overlap")
    if target.name != NAME:
        raise ValueError("Invalid exact target")
    if target.exists() and not replace:
        raise FileExistsError("Skill already exists; use --replace for a backed-up update")
    files = bundle_files(source)
    plan = {"platform": platform, "scope": scope, "target": str(target),
            "version": manifest_version(source), "file_count": len(files), "dry_run": dry_run}
    if dry_run:
        return plan
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".software-skill-install-", dir=target.parent))
    backup = None
    try:
        for path in files:
            out = temporary / path.relative_to(source)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(file_bytes(path, source, "workbuddy" if platform == "workbuddy" else "standard"))
        if target.exists():
            backup = target.parent.parent / "software-skill-backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") / NAME
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.resolve().is_relative_to(target):
                raise ValueError("Backup must stay outside target")
            shutil.move(str(target), str(backup))
        temporary.rename(target)
    except Exception:
        if backup and backup.exists() and not target.exists():
            shutil.move(str(backup), str(target))
        raise
    finally:
        if temporary.exists():
            # Exact freshly-created temporary directory only.
            assert temporary.parent.resolve() == target.parent.resolve()
            assert temporary.name.startswith(".software-skill-install-")
            shutil.rmtree(temporary)
    plan.update(dry_run=False, backup=str(backup) if backup else None)
    return plan

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--platform", choices=["codex", "workbuddy", "deepseek", "agents"], required=True)
    p.add_argument("--scope", choices=["user", "project"], default="user")
    p.add_argument("--project")
    p.add_argument("--skills-dir", help="Explicit skill root already discovered by your host")
    p.add_argument("--replace", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    try:
        print(json.dumps(install(a.platform, a.scope, a.project, skills_dir=a.skills_dir,
                                 replace=a.replace, dry_run=a.dry_run), ensure_ascii=False))
    except (OSError, ValueError) as exc:
        p.exit(1, f"Install stopped: {exc}\n")

if __name__ == "__main__":
    main()
