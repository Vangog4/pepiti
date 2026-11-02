"""Validation/parsing of free-text passport fields. Pure, no I/O."""

from __future__ import annotations

from datetime import date

LIST_FIELDS = {"allergies", "chronic_conditions"}
SPECIAL_FIELDS = LIST_FIELDS | {"weight_kg", "birth_date"}
MAX_LIST_ITEMS = 10
MAX_ITEM_LEN = 40


class PassportValueError(ValueError):
    """User input cannot be stored in this field."""


def parse_passport_value(field: str, raw: str, today: date | None = None) -> object:
    text = (raw or "").strip()
    if not text:
        raise PassportValueError("empty")
    if field in LIST_FIELDS:
        if text.lower() in {"нет", "-", "no", "none"}:
            return []
        items: list[str] = []
        for part in text.replace(";", ",").replace("\n", ",").split(","):
            item = " ".join(part.split())[:MAX_ITEM_LEN]
            if item and item.lower() not in {i.lower() for i in items}:
                items.append(item)
        if not items:
            raise PassportValueError("empty")
        return items[:MAX_LIST_ITEMS]
    if field == "weight_kg":
        try:
            value = float(
                text.lower().replace("кг", "").replace("kg", "").replace(",", ".").strip()
            )
        except ValueError as exc:
            raise PassportValueError("weight") from exc
        if not 0.3 <= value <= 120:
            raise PassportValueError("weight")
        return round(value, 1)
    if field == "birth_date":
        today = today or date.today()
        try:
            d, m, y = (int(x) for x in text.replace("/", ".").replace("-", ".").split("."))
            value = date(y, m, d)
        except ValueError as exc:
            raise PassportValueError("date") from exc
        if value > today or (today.year - value.year) > 30:
            raise PassportValueError("date")
        return value
    raise PassportValueError("unknown field")
