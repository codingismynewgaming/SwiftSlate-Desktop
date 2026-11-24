"""Validation tests for the bundled commands.json file."""

import json
from pathlib import Path
import unittest


class CommandsFileTest(unittest.TestCase):
    def test_commands_json_is_valid_german_defaults(self):
        path = Path(__file__).parents[1] / "commands.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 12)

        valid_types = {"ai", "replacer", "replacer-shell"}
        seen_triggers = set()

        for entry in data:
            self.assertIsInstance(entry, dict)
            trigger = entry.get("trigger")
            self.assertIsInstance(trigger, str)
            self.assertTrue(trigger)
            self.assertFalse(any(ch.isspace() for ch in trigger), f"Whitespace in trigger: {trigger!r}")
            self.assertNotEqual(trigger.lower(), "ip")
            self.assertNotIn(trigger.lower(), seen_triggers)
            seen_triggers.add(trigger.lower())

            cmd_type = entry.get("type")
            self.assertIn(cmd_type, valid_types)

            if cmd_type == "ai":
                self.assertIsInstance(entry.get("prompt"), str)
                self.assertTrue(entry["prompt"].strip())
            else:
                self.assertIsInstance(entry.get("value"), str)
                self.assertTrue(entry["value"].strip())


if __name__ == "__main__":
    unittest.main()
