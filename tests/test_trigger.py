"""Pure-logic tests for trigger detection and field context validation."""

import ast
from pathlib import Path
import unittest


def load_trigger_helpers():
    source_path = Path(__file__).parents[1] / "SwiftSlate.pyw"
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    names = {"find_trigger", "trigger_context_ok"}
    body = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace


class TriggerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_trigger_helpers()
        cls.find_trigger = staticmethod(cls.helpers["find_trigger"])
        cls.trigger_context_ok = staticmethod(cls.helpers["trigger_context_ok"])
        cls.names = ["fix", "de", "en", "kurz", "datum", "undo"]

    def test_valid_triggers(self):
        self.assertEqual(self.find_trigger("ich hab das .fix", ".", self.names), "fix")
        self.assertEqual(self.find_trigger(".fix", ".", self.names, buffer_truncated=False), "fix")
        self.assertEqual(self.find_trigger("Hallo\u00a0.de", ".", self.names), "de")
        self.assertEqual(self.find_trigger("Text .translate:EN", ".", self.names), "translate:en")

    def test_rejected_triggers(self):
        cases = [
            "Satz.fix",
            "siehe example.de",
            "https://x.de",
            "z.B.",
            "usw.",
            "notiz.txt",
            "Version 3.5",
            "warte ...",
            "warte ...fix",
            "Text .unbekannt",
            "Text .",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertIsNone(self.find_trigger(text, ".", self.names))
        self.assertIsNone(self.find_trigger(".fix", ".", self.names, buffer_truncated=True))

    def test_longest_match_wins(self):
        self.assertEqual(self.find_trigger("a .fixit", ".", ["fix", "fixit"]), "fixit")

    def test_custom_question_prefix(self):
        self.assertEqual(self.find_trigger("ich hab das ?fix", "?", self.names), "fix")
        self.assertIsNone(self.find_trigger("warum?fix", "?", self.names))

    def test_trigger_context_ok(self):
        self.assertFalse(self.trigger_context_ok("abc example.de", ".de"))
        self.assertTrue(self.trigger_context_ok("abc .de", ".de"))
        self.assertTrue(self.trigger_context_ok("Abc .Fix", ".fix"))
        self.assertTrue(self.trigger_context_ok(".de", ".de"))
        self.assertTrue(self.trigger_context_ok("abc .de\r\n", ".de"))


if __name__ == "__main__":
    unittest.main()
