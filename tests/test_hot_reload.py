"""Hot Reload: bei ungültiger Config bleibt der letzte gültige Stand aktiv."""

import ast
from pathlib import Path
import unittest


def load_helpers():
    source_path = Path(__file__).parents[1] / "SwiftSlateJMKEdition.pyw"
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    names = {"ready_after_failed_load", "hot_reload_failure_message"}
    body = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in names]
    namespace = {}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace


class HotReloadStateTests(unittest.TestCase):
    def setUp(self):
        ns = load_helpers()
        self.ready = ns["ready_after_failed_load"]
        self.msg = ns["hot_reload_failure_message"]

    def test_initial_start_is_not_ready(self):
        self.assertFalse(self.ready(False, True))
        self.assertFalse(self.ready(True, True))

    def test_hot_reload_keeps_last_valid_state(self):
        self.assertTrue(self.ready(True, False))

    def test_hot_reload_without_valid_state_stays_not_ready(self):
        self.assertFalse(self.ready(False, False))

    def test_message_names_reason_and_keeps_state(self):
        text = self.msg("Endpoint fehlt.")
        self.assertIn("Endpoint fehlt.", text)
        self.assertIn("Letzter gültiger Stand bleibt aktiv", text)

    def test_message_without_reason(self):
        self.assertIn("unbekannter Fehler", self.msg(""))


if __name__ == "__main__":
    unittest.main()
