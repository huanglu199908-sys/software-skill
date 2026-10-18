import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from install import install, destination
from build_packages import build
from export_prompt import render, STAGES
from skill_bundle import NAME, bundle_files

class PortabilityTests(unittest.TestCase):
    def test_platform_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            for host, folder in [("codex", ".agents"), ("deepseek", ".dsh"), ("workbuddy", ".codebuddy")]:
                self.assertEqual(destination(host, "user", home=home), home / folder / "skills" / NAME)
            self.assertEqual(destination("workbuddy", "project", project=home), home / ".codebuddy/skills" / NAME)

    def test_install_collision_and_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = install("codex", home=tmp); path = Path(info["target"])
            self.assertIn("name: software-skill", (path / "SKILL.md").read_text(encoding="utf-8"))
            (path / "local-note.txt").write_text("preserve me")
            with self.assertRaises(FileExistsError): install("codex", home=tmp)
            new = install("codex", home=tmp, replace=True)
            self.assertEqual((Path(new["backup"]) / "local-note.txt").read_text(), "preserve me")
            self.assertFalse((path / "local-note.txt").exists())

    def test_dry_run_has_no_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = install("deepseek", home=tmp, dry_run=True)
            self.assertFalse(Path(info["target"]).exists())
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_workbuddy_metadata_and_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = install("workbuddy", "project", project=tmp); p = Path(out["target"])
            text = (p / "SKILL.md").read_text(encoding="utf-8")
            for key in ["description_zh", "description_en", "version", "author"]:
                self.assertRegex(text, re.compile(r"^" + key + ":", re.M))
            self.assertTrue((p / "references/format-profile.json").exists())
            self.assertEqual(text.split("---", 2)[2], (ROOT / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[2])

    def test_archives_and_resource_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = build(tmp)
            for item in result:
                with zipfile.ZipFile(Path(tmp) / item["file"]) as z:
                    self.assertTrue(all(n.startswith("software-skill/") and ".." not in n.split("/") for n in z.namelist()))
                    self.assertIn("software-skill/SKILL.md", z.namelist())
                    self.assertIn("software-skill/scripts/materials.py", z.namelist())
                    self.assertIn("software-skill/assets/material-input.example.json", z.namelist())
                    self.assertIn("software-skill/requirements.txt", z.namelist())
                    self.assertFalse(any(".git/" in n or "__pycache__" in n or n.endswith(".env") for n in z.namelist()))
                    manifest = z.read("software-skill/SKILL.md").decode("utf-8")
                    self.assertEqual("description_zh:" in manifest, item["platform"] == "workbuddy")
            self.assertEqual(build(tmp), result)

    def test_relative_references_resolve(self):
        for p in bundle_files():
            if p.suffix != ".md": continue
            for target in re.findall(r"\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"): continue
                self.assertTrue((p.parent / target.split("#")[0]).is_file(), f"{p.name}: {target}")

    def test_stage_export_and_explicit_model(self):
        for stage in STAGES:
            data = json.loads(render(stage, "本地核验", "messages"))
            self.assertTrue(all(x["role"] == "user" for x in data["messages"]))
            self.assertIn("BEGIN SKILL.md", data["messages"][0]["content"])
            self.assertEqual(data["messages"][-1]["content"], "本地核验")
        with self.assertRaises(ValueError): render("audit", "test", "request")
        request = json.loads(render("audit", "test", "request", "explicit-model-id"))
        self.assertEqual(request["model"], "explicit-model-id")
        self.assertIn("format-profile.json", request["messages"][0]["content"])

    def test_install_rejects_source_overlap(self):
        with self.assertRaises(ValueError): install("codex", skills_dir=ROOT)

if __name__ == "__main__":
    unittest.main()
