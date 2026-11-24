"""Pure-logic tests for robust OpenAI-compatible response parsing."""

import ast
import re
from pathlib import Path
import unittest


def load_robust_helpers():
    source_path = Path(__file__).parents[1] / "SwiftSlate.pyw"
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    names = {"extract_openai_content", "strip_think_block"}
    body = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {"re": re}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace


class ApiRobustTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_robust_helpers()
        cls.extract = staticmethod(cls.helpers["extract_openai_content"])
        cls.strip_think = staticmethod(cls.helpers["strip_think_block"])

    def test_extract_valid_content(self):
        choice = {"message": {"content": "  Hallo Welt  "}, "finish_reason": "stop"}
        text, reason = self.extract(choice)
        self.assertEqual(text, "Hallo Welt")
        self.assertIsNone(reason)

    def test_extract_reasoning_only_content_null(self):
        choice = {
            "message": {"content": None, "reasoning_content": "Ich denke nach..."},
            "finish_reason": "stop",
        }
        text, reason = self.extract(choice)
        self.assertIsNone(text)
        self.assertIn("nur Denktext", reason)

    def test_extract_reasoning_field_alternative(self):
        choice = {
            "message": {"content": "", "reasoning": "Thinking..."},
            "finish_reason": "stop",
        }
        text, reason = self.extract(choice)
        self.assertIsNone(text)
        self.assertIn("nur Denktext", reason)

    def test_extract_finish_reason_length(self):
        choice = {
            "message": {"content": None, "reasoning_content": "Thinking..."},
            "finish_reason": "length",
        }
        text, reason = self.extract(choice)
        self.assertIsNone(text)
        self.assertIn("abgeschnitten", reason)

    def test_extract_empty_content(self):
        choice = {"message": {"content": "   "}, "finish_reason": "stop"}
        text, reason = self.extract(choice)
        self.assertIsNone(text)
        self.assertEqual(reason, "Leere Antwort vom Modell.")

    def test_strip_think_block_leading(self):
        self.assertEqual(self.strip_think("<think>abc</think>\nHallo"), "Hallo")
        self.assertEqual(self.strip_think("  <THINK>\nmulti\nline\n</THINK>  Ergebnis"), "Ergebnis")

    def test_strip_think_block_without_think(self):
        self.assertEqual(self.strip_think("Normaler Text"), "Normaler Text")

    def test_strip_think_block_only_think(self):
        self.assertEqual(self.strip_think("<think>nur denken</think>"), "")


if __name__ == "__main__":
    unittest.main()
