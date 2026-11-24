"""Pure-logic tests for settings validation and atomic JSON writing."""

import ast
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
import urllib.parse


def load_settings_helpers():
    source_path = Path(__file__).parents[1] / "SwiftSlateJMKEdition.pyw"
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    names = {"write_json_atomic", "validate_settings"}
    body = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {
        "os": os,
        "json": json,
        "math": math,
        "tempfile": tempfile,
        "urllib": urllib,
    }
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace


class SettingsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_settings_helpers()
        cls.write_atomic = staticmethod(cls.helpers["write_json_atomic"])
        cls.validate = staticmethod(cls.helpers["validate_settings"])

    def test_write_json_atomic_creates_and_replaces_without_tmp_leftovers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "config.json"
            self.write_atomic(str(target), {"a": 1, "umlaut": "ü"})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"a": 1, "umlaut": "ü"})

            self.write_atomic(str(target), {"a": 2})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"a": 2})
            leftovers = [p.name for p in Path(tmpdir).iterdir() if p.name != "config.json"]
            self.assertEqual(leftovers, [])

    def test_validate_settings_valid(self):
        valid = {
            "provider": "custom",
            "endpoint": "https://api.example.com/v1",
            "model": "gpt-4o-mini",
            "temperature": "0.3",
            "prefix": ".",
            "trigger_delay_ms": "1000",
        }
        self.assertEqual(self.validate(valid), [])

    def test_validate_settings_rejects_invalid_rules(self):
        base = {
            "provider": "custom",
            "endpoint": "https://api.example.com/v1",
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "prefix": ".",
            "trigger_delay_ms": 1000,
        }
        for field, bad_val in [
            ("provider", "invalid"),
            ("endpoint", "ftp://example.com"),
            ("model", "   "),
            ("temperature", 2.5),
            ("prefix", "ab"),
            ("prefix", " "),
            ("trigger_delay_ms", 9000),
            ("trigger_delay_ms", -1),
        ]:
            with self.subTest(field=field, bad_val=bad_val):
                case = dict(base)
                case[field] = bad_val
                errs = self.validate(case)
                self.assertTrue(len(errs) >= 1)


if __name__ == "__main__":
    unittest.main()
