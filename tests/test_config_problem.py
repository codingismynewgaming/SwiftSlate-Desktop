"""Pure-logic tests for config_problem()."""

import ast
from pathlib import Path
import unittest


def load_config_problem():
    source_path = Path(__file__).parents[1] / "SwiftSlateJMKEdition.pyw"
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    body = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "config_problem"]
    namespace = {}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace["config_problem"]


class ConfigProblemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_problem = staticmethod(load_config_problem())

    def test_missing_endpoint_for_custom(self):
        cfg = {"provider": "custom", "endpoint": "", "model": "llama3", "api_keys": []}
        self.assertEqual(self.config_problem(cfg), "Endpoint fehlt.")

    def test_empty_model(self):
        cfg = {"provider": "custom", "endpoint": "http://localhost:11434/v1", "model": "  ", "api_keys": []}
        self.assertEqual(self.config_problem(cfg), "Modell fehlt.")

    def test_gemini_without_key(self):
        cfg = {"provider": "gemini", "model": "gemini-2.5-flash", "api_keys": []}
        self.assertEqual(self.config_problem(cfg), "API Key fehlt.")

    def test_custom_without_key_is_ok(self):
        cfg = {"provider": "custom", "endpoint": "http://localhost:11434/v1", "model": "llama3", "api_keys": []}
        self.assertIsNone(self.config_problem(cfg))

    def test_valid_gemini_config(self):
        cfg = {"provider": "gemini", "model": "gemini-2.5-flash", "api_keys": ["sk-test"]}
        self.assertIsNone(self.config_problem(cfg))


if __name__ == "__main__":
    unittest.main()
