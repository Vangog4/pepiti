"""Weight trend from the dog's OWN history. No breed norms: we do not have trusted tables,
so we never claim a dog is "over/underweight", only that its weight changed a lot."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.logic.rules import rule


def weight_trend(entries: list[Any], today: date) -> dict:
    rows = sorted(
        (e for e in entries if e.weight_kg and e.weight_kg > 0),
        key=lambda e: e.local_date,
        reverse=True,
    )
    out: dict = {
        "last": None,
        "last_date": None,
        "prev": None,
        "delta_kg": None,
        "delta_pct": None,
        "alert": None,
    }
    if not rows:
        return out
    latest = rows[0]
    out["last"], out["last_date"] = latest.weight_kg, latest.local_date
    target = int(rule("weight.compare_days", 30))
    min_gap = int(rule("weight.min_gap_days", 7))
    older = [e for e in rows[1:] if (latest.local_date - e.local_date).days >= min_gap]
    if not older:
        return out
    prev = min(older, key=lambda e: abs((latest.local_date - e.local_date).days - target))
    out["prev"] = prev.weight_kg
    out["delta_kg"] = round(latest.weight_kg - prev.weight_kg, 1)
    out["delta_pct"] = round(out["delta_kg"] / prev.weight_kg * 100, 1)
    threshold = float(rule("weight.alert_pct", 10))
    if out["delta_pct"] >= threshold:
        out["alert"] = "gain"
    elif out["delta_pct"] <= -threshold:
        out["alert"] = "loss"
    return out
