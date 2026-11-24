"""Pure-logic tests for trigger_delay_ms parsing."""

import ast
import math
from pathlib import Path
import unittest


def load_trigger_delay_helper():
    source_path = Path(__file__).parents[1] / "SwiftSlate.pyw"
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    names = {"parse_trigger_delay"}
    body = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {"math": math}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace["parse_trigger_delay"]


class TriggerDelayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parse_delay = staticmethod(load_trigger_delay_helper())

    def test_parse_trigger_delay_cases(self):
        self.assertEqual(self.parse_delay(None), 1000)
        self.assertEqual(self.parse_delay(True), 1000)
        self.assertEqual(self.parse_delay(-5), 0)
        self.assertEqual(self.parse_delay(99999), 5000)
        self.assertEqual(self.parse_delay(1500.7), 1500)
        self.assertEqual(self.parse_delay("abc"), 1000)
        self.assertEqual(self.parse_delay(float("nan")), 1000)
        self.assertEqual(self.parse_delay(float("inf")), 1000)
        self.assertEqual(self.parse_delay(0), 0)
        self.assertEqual(self.parse_delay(1000), 1000)


if __name__ == "__main__":
    unittest.main()
