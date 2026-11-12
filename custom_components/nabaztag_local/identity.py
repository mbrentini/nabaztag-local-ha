"""Pure helpers for routing status and physical events to the right rabbit."""

from __future__ import annotations

from typing import Any


def normalize_mac(value: str | None) -> str:
    """Normalize MAC values from the API, HA events or setup form."""
    return (value or "").lower().replace(":", "").replace("-", "").strip()


def rabbit_status(data: dict[str, Any], configured_mac: str | None) -> dict[str, Any]:
    """Get status of the configured rabbit, never of an arbitrary other rabbit."""
    bunnies = data.get("bunnies") or {}
    selected = normalize_mac(configured_mac)
    if selected:
        for mac, rabbit in bunnies.items():
            if normalize_mac(mac) == selected:
                return rabbit if isinstance(rabbit, dict) else {}
        return {}
    if len(bunnies) == 1:
        one = next(iter(bunnies.values()))
        return one if isinstance(one, dict) else {}
    return {}


def event_for_rabbit(
    data: dict[str, Any], configured_mac: str | None, entries: int
) -> bool:
    """Do not broadcast unidentified physical events to several rabbits."""
    event_mac = normalize_mac(
        data.get("mac") or data.get("sn") or data.get("rabbit_mac")
    )
    selected = normalize_mac(configured_mac)
    if event_mac and selected:
        return event_mac == selected
    if event_mac and not selected:
        return entries == 1
    return entries == 1
