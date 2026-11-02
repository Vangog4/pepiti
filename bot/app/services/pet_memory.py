"""Pure helpers that turn a dog's passport + remembered facts into prompt context."""

from __future__ import annotations

from datetime import date
from typing import Any

MAX_FACTS_IN_PROMPT = 20
MAX_FACTS_STORED = 100


def _age_text(pet: Any, today: date) -> str | None:
    born = getattr(pet, "birth_date", None)
    if born:
        months = (today.year - born.year) * 12 + (today.month - born.month)
        if months >= 24:
            return f"{months // 12} г"
        return f"{max(months, 0)} мес"
    return getattr(pet, "age_category", None)


def pet_memory_block(pet: Any, facts: list[str], today: date | None = None) -> str:
    """Compact "what we know about the dog" block for the coach prompt."""
    today = today or date.today()
    parts: list[str] = [f"Dog: {pet.name}"]
    if getattr(pet, "breed", None):
        parts.append(f"breed {pet.breed}")
    age = _age_text(pet, today)
    if age:
        parts.append(f"age {age}")
    if getattr(pet, "weight_kg", None):
        parts.append(f"weight {pet.weight_kg} kg")
    lines = ["; ".join(parts)]
    if getattr(pet, "allergies", None):
        lines.append("Allergies: " + ", ".join(pet.allergies))
    if getattr(pet, "chronic_conditions", None):
        lines.append("Chronic conditions: " + ", ".join(pet.chronic_conditions))
    if getattr(pet, "health_notes", None):
        lines.append(f"Health notes: {pet.health_notes}")
    shown = facts[:MAX_FACTS_IN_PROMPT]
    if shown:
        lines.append("Remembered facts:")
        lines.extend(f"- {f}" for f in shown)
    return "\n".join(lines)


def merge_new_facts(known: list[str], new: list[str]) -> list[str]:
    """New facts not already known (case/whitespace-insensitive), order preserved, no dups."""
    seen = {" ".join(k.lower().split()) for k in known}
    out: list[str] = []
    for f in new:
        key = " ".join(f.lower().split())
        if key and key not in seen:
            seen.add(key)
            out.append(" ".join(f.split()))
    return out
