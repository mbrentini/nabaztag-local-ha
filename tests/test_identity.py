"""Pure unit tests: no Home Assistant runtime required."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "custom_components/nabaztag_local/identity.py"
SPEC = importlib.util.spec_from_file_location("identity", MODULE)
assert SPEC is not None and SPEC.loader is not None
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)


class IdentityTests(unittest.TestCase):
    def test_normalize_mac(self) -> None:
        self.assertEqual(identity.normalize_mac("00:19:DB:9C:12:AE"), "0019db9c12ae")
        self.assertEqual(identity.normalize_mac("00-19-db-9c-12-ae"), "0019db9c12ae")
        self.assertEqual(identity.normalize_mac(None), "")

    def test_select_only_configured_bunny(self) -> None:
        data = {
            "bunnies": {
                "0019db9c12ae": {"resource": "asleep", "alive": True},
                "0019db9c12af": {"resource": "awake", "alive": False},
            }
        }
        self.assertEqual(identity.rabbit_status(data, "00:19:DB:9C:12:AE")["resource"], "asleep")
        self.assertEqual(identity.rabbit_status(data, "0019db9c12ff"), {})
        self.assertEqual(identity.rabbit_status(data, None), {})

    def test_one_bunny_can_be_implicit(self) -> None:
        data = {"bunnies": {"0019db9c12ae": {"resource": "idle"}}}
        self.assertEqual(identity.rabbit_status(data, None)["resource"], "idle")

    def test_events_do_not_leak_between_rabbits(self) -> None:
        event = {"type": "rfid", "mac": "00:19:DB:9C:12:AE", "tag": "abc"}
        self.assertTrue(identity.event_for_rabbit(event, "0019db9c12ae", 2))
        self.assertFalse(identity.event_for_rabbit(event, "0019db9c12af", 2))
        self.assertFalse(identity.event_for_rabbit(event, None, 2))
        self.assertTrue(identity.event_for_rabbit({"type": "button"}, None, 1))
        self.assertFalse(identity.event_for_rabbit({"type": "button"}, None, 2))


if __name__ == "__main__":
    unittest.main()
