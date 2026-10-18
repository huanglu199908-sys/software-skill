"""Focused invariants: loss, whitespace, drift, ordering, path bounds, and document binding."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from source_evidence import snapshot, check, compare, digest


class SourceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "项目"
        self.project.mkdir()
        # Unknown extension, Chinese, comment, tab, blank string line and closing delimiter.
        self.source = self.project / "业务.custom"
        self.source.write_bytes('def f():\r\n\t# 保留说明\r\n\ttext = """a  b\r\n\r\nend"""\r\n\treturn text\r\n'.encode("utf-8"))
        self.selection = self.root / "selection.json"
        self.selection.write_text(json.dumps(["业务.custom"], ensure_ascii=False), encoding="utf-8")
        self.manifest = self.root / "snapshot.json"
        snapshot(self.project, self.selection, self.manifest)
        self.doc = self.root / "material.fixture"
        self.doc.write_bytes(b"document readback fixture, not a real DOCX")
        record = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.export = {"snapshot_sha256": digest(self.manifest.read_bytes()),
                       "document": {"path": str(self.doc), "sha256": digest(self.doc.read_bytes())},
                       "scope": "all-selected-source-lines", "tab_expansion": 0,
                       "rows": [{"file": f["path"], "line": i, "segments": [line]}
                                for f in record["files"] for i, line in enumerate(f["lines"], 1)]}

    def result(self, export=None):
        path = self.root / "readback.json"
        path.write_text(json.dumps(export or self.export, ensure_ascii=False), encoding="utf-8")
        return compare(self.manifest, path)

    def test_intact_unknown_extension_unicode_and_crlf(self):
        self.assertTrue(check(self.manifest)["ok"])
        self.assertTrue(self.result()["ok"])

    def test_comment_or_closing_delimiter_loss_fails(self):
        for i in (1, 4):
            export = copy.deepcopy(self.export)
            export["rows"][i]["segments"] = [""]
            self.assertFalse(self.result(export)["ok"])

    def test_indent_and_string_spaces_are_significant(self):
        for before, after in (("\t", ""), ("a  b", "a b")):
            export = copy.deepcopy(self.export)
            export["rows"][2]["segments"][0] = export["rows"][2]["segments"][0].replace(before, after)
            self.assertFalse(self.result(export)["ok"])

    def test_deterministic_segments_and_explicit_tabs(self):
        export = copy.deepcopy(self.export)
        export["tab_expansion"] = 4
        for row in export["rows"]:
            text = row["segments"][0].expandtabs(4)
            row["segments"] = [text[:3], text[3:]]
        self.assertTrue(self.result(export)["ok"])

    def test_blank_line_missing_or_order_changed_fails(self):
        export = copy.deepcopy(self.export)
        export["rows"].pop(3)
        self.assertFalse(self.result(export)["ok"])
        export = copy.deepcopy(self.export)
        export["rows"][0], export["rows"][1] = export["rows"][1], export["rows"][0]
        self.assertFalse(self.result(export)["ok"])

    def test_source_drift_and_deletion(self):
        self.source.write_bytes(self.source.read_bytes() + b"# changed\n")
        self.assertFalse(check(self.manifest)["ok"])
        self.assertEqual(self.result()["stage"], "source-check")
        self.source.unlink()
        self.assertFalse(check(self.manifest)["ok"])

    def test_document_or_snapshot_binding_change(self):
        export = copy.deepcopy(self.export)
        export["snapshot_sha256"] = "wrong"
        self.assertFalse(self.result(export)["ok"])
        self.doc.write_bytes(b"new revision")
        self.assertFalse(self.result()["ok"])

    def test_duplicate_escape_and_absolute_rejected(self):
        for names in (["业务.custom", "业务.custom"], ["../selection.json"], [str(self.source)]):
            self.selection.write_text(json.dumps(names), encoding="utf-8")
            with self.assertRaises(ValueError):
                snapshot(self.project, self.selection, self.root / "other.json")

    def test_no_overwrite(self):
        before = self.manifest.read_bytes()
        with self.assertRaises(FileExistsError):
            snapshot(self.project, self.selection, self.manifest)
        self.assertEqual(before, self.manifest.read_bytes())

    def test_empty_file_and_binary_rejection(self):
        self.source.write_bytes(b"")
        out = self.root / "empty.json"
        result = snapshot(self.project, self.selection, out)
        self.assertEqual(result["physical_lines"], 0)
        self.assertTrue(check(out)["ok"])
        self.source.write_bytes(b"\x00binary")
        with self.assertRaises(ValueError):
            snapshot(self.project, self.selection, self.root / "binary.json")

    def test_partial_page_mode_not_misreported_as_complete(self):
        self.export["scope"] = "front-back-pages"
        with self.assertRaises(ValueError):
            self.result()


if __name__ == "__main__":
    unittest.main(verbosity=2)
