"""Tray icon callback decoding (regression for v1.0.0: clicks on the icon did nothing)."""

import ast
from pathlib import Path
import unittest


def load_tray_helper():
    source_path = Path(__file__).parents[1] / "SwiftSlateJMKEdition.pyw"
    module = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    wanted_names = {"WM_LBUTTONUP", "WM_LBUTTONDBLCLK", "WM_RBUTTONUP", "WM_CONTEXTMENU",
                    "NIN_SELECT", "NIN_KEYSELECT"}
    body = [
        node for node in module.body
        if (isinstance(node, ast.FunctionDef) and node.name == "tray_event_action")
        or (isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id in wanted_names for t in node.targets))
    ]
    namespace = {}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace


ICON_ID = 1001


def v4(event):
    # NOTIFYICON_VERSION_4: lParam = MAKELPARAM(event, icon id)
    return (ICON_ID << 16) | event


class TrayEventTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = load_tray_helper()
        cls.action = staticmethod(cls.ns["tray_event_action"])

    def test_v4_context_menu_opens_menu(self):
        self.assertEqual(self.action(v4(self.ns["WM_CONTEXTMENU"]), True), "menu")

    def test_v4_left_click_and_double_click_open_settings(self):
        self.assertEqual(self.action(v4(self.ns["NIN_SELECT"]), True), "settings")
        self.assertEqual(self.action(v4(self.ns["NIN_KEYSELECT"]), True), "settings")
        self.assertEqual(self.action(v4(self.ns["WM_LBUTTONDBLCLK"]), True), "settings")

    def test_v4_raw_mouse_messages_are_ignored(self):
        # Right button up is followed by WM_CONTEXTMENU; handling both would open two menus.
        self.assertIsNone(self.action(v4(self.ns["WM_RBUTTONUP"]), True))
        self.assertIsNone(self.action(v4(self.ns["WM_LBUTTONUP"]), True))
        self.assertIsNone(self.action(v4(0x0200), True))  # WM_MOUSEMOVE

    def test_v4_icon_id_in_high_word_does_not_break_matching(self):
        # v1.0.0 compared the whole lParam with WM_RBUTTONUP, which never matched.
        self.assertNotEqual(v4(self.ns["WM_RBUTTONUP"]), self.ns["WM_RBUTTONUP"])
        self.assertEqual(self.action(v4(self.ns["WM_CONTEXTMENU"]), True), "menu")

    def test_legacy_version(self):
        self.assertEqual(self.action(self.ns["WM_RBUTTONUP"], False), "menu")
        self.assertEqual(self.action(self.ns["WM_LBUTTONUP"], False), "settings")
        self.assertEqual(self.action(self.ns["WM_LBUTTONDBLCLK"], False), "settings")
        self.assertIsNone(self.action(0x0200, False))


if __name__ == "__main__":
    unittest.main()
