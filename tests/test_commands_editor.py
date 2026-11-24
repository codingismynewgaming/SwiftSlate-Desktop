"""Pure-logic tests for command editor validation."""

import ast
from pathlib import Path
import unittest


def load_commands_editor_helpers():
    source_path = Path(__file__).parents[1] / "SwiftSlate.pyw"
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    names = {"validate_commands", "find_command_prefix_warnings"}
    body = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace


class CommandsEditorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_commands_editor_helpers()
        cls.validate = staticmethod(cls.helpers["validate_commands"])
        cls.prefix_warnings = staticmethod(cls.helpers["find_command_prefix_warnings"])

    def test_valid_commands(self):
        cmds = [
            {"trigger": "fix", "type": "ai", "prompt": "Korrigieren."},
            {"trigger": "sig", "type": "replacer-text", "value": "Viele Grüße"},
            {"trigger": "datum", "type": "replacer-shell", "value": "date"},
        ]
        self.assertEqual(self.validate(cmds), [])

    def test_rejects_invalid_commands(self):
        cases = [
            [{"trigger": "", "type": "ai", "prompt": "x"}],
            [{"trigger": "a" * 51, "type": "ai", "prompt": "x"}],
            [{"trigger": "mit leerzeichen", "type": "ai", "prompt": "x"}],
            [{"trigger": ".fix", "type": "ai", "prompt": "x"}],
            [{"trigger": "fix", "type": "ai", "prompt": "x"}, {"trigger": "FIX", "type": "ai", "prompt": "y"}],
            [{"trigger": "undo", "type": "ai", "prompt": "x"}],
            [{"trigger": "translate", "type": "ai", "prompt": "x"}],
            [{"trigger": "translate:de", "type": "ai", "prompt": "x"}],
            [{"trigger": "fix", "type": "ai", "prompt": "  "}],
            [{"trigger": "datum", "type": "replacer-shell", "value": ""}],
            [{"trigger": f"cmd{i}", "type": "ai", "prompt": "x"} for i in range(101)],
        ]
        for cmds in cases:
            with self.subTest(cmds=cmds[0]):
                self.assertTrue(len(self.validate(cmds)) >= 1)

    def test_prefix_warnings(self):
        cmds = [
            {"trigger": "fix", "type": "ai", "prompt": "a"},
            {"trigger": "fixit", "type": "ai", "prompt": "b"},
        ]
        warns = self.prefix_warnings(cmds, ".")
        self.assertEqual(len(warns), 1)
        self.assertIn(".fix ist Anfang von .fixit", warns[0])


if __name__ == "__main__":
    unittest.main()
