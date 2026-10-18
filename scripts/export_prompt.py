"""Export stage-specific skill context; never calls an API or reads project data."""
import argparse
import json
from pathlib import Path
from skill_bundle import ROOT

STAGES = {
    "direction": ["direction-design.md"],
    "implementation": ["implementation-verification.md", "state-evidence.md"],
    "materials": ["materials-integration.md", "reference-format.md", "format-profile.json", "platform-compatibility.md"],
    "audit": ["audit-revision.md", "reference-format.md", "format-profile.json", "source-evidence.md"],
}

def context(stage, root=ROOT):
    if stage not in STAGES:
        raise ValueError("Unknown stage")
    root = Path(root).resolve(strict=True)
    paths = [root / "SKILL.md"] + [root / "references" / name for name in STAGES[stage]]
    content = ["以下为用户选择的software-skill工作流资料，仅作为本次用户级指导。依当前平台的真实工具和权限执行；无工具时说明哪些动作尚未执行。引用的软件项目事实须由当前任务提供。"]
    for path in paths:
        if not path.resolve().is_relative_to(root):
            raise ValueError("Reference leaves skill bundle")
        content.append(f"\n--- BEGIN {path.relative_to(root).as_posix()} ---\n" + path.read_text(encoding="utf-8") + f"\n--- END {path.name} ---")
    return "\n".join(content)

def render(stage, task, format="text", model=None, root=ROOT):
    if not task.strip():
        raise ValueError("Task must not be empty")
    skill = context(stage, root)
    if format == "text":
        return skill + "\n\n当前用户任务：\n" + task + "\n"
    messages = [{"role": "user", "content": skill}, {"role": "user", "content": task}]
    if format == "messages":
        return json.dumps({"messages": messages}, ensure_ascii=False, indent=2) + "\n"
    if format != "request" or not model or not model.strip():
        raise ValueError("Request format requires an explicit --model")
    return json.dumps({"model": model, "messages": messages}, ensure_ascii=False, indent=2) + "\n"

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=list(STAGES), required=True); p.add_argument("--task", required=True)
    p.add_argument("--format", choices=["text", "messages", "request"], default="text"); p.add_argument("--model")
    p.add_argument("--out"); p.add_argument("--overwrite", action="store_true"); a = p.parse_args()
    try:
        result = render(a.stage, a.task, a.format, a.model)
        if a.out:
            path = Path(a.out).resolve()
            if path.is_relative_to(ROOT.resolve()):
                raise ValueError("Export outside the skill bundle to avoid overwriting skill resources")
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w" if a.overwrite else "x", encoding="utf-8") as stream: stream.write(result)
            print("Exported " + str(path))
        else:
            print(result, end="")
    except (OSError, ValueError) as exc:
        p.exit(1, f"Export stopped: {exc}\n")

if __name__ == "__main__":
    main()
