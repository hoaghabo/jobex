# app/features/event/normalizers.py

from __future__ import annotations

from typing import Any


def extract_events_list(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, list):
        return response

    if isinstance(response, dict):
        results = response.get("results")
        if isinstance(results, list):
            return results

    return []


def extract_event_detail(response: Any) -> dict[str, Any] | None:
    if isinstance(response, dict):
        return response

    return None
