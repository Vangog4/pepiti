"""Dog passport as a single PDF for the vet. Data collection is pure; rendering uses fpdf2."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from app.cards.render import strip_unrenderable  # the bundled font has no emoji glyphs
from app.i18n import normalize_locale, t
from app.services.health import KINDS, latest_per_kind
from app.services.pet_memory import _age_text

MAX_HISTORY = 30
MAX_FACTS = 20
_ASSETS = Path(__file__).resolve().parent.parent / "assets"


def _clean(value: Any, limit: int = 400) -> str:
    return strip_unrenderable(str(value or ""))[:limit]


def passport_pdf_data(pet: Any, events: list, facts: list[str], today: date) -> dict:
    cur = latest_per_kind(events)
    history = sorted(events, key=lambda e: (e.done_at, e.id), reverse=True)[:MAX_HISTORY]
    return {
        "name": _clean(pet.name, 80),
        "breed": _clean(getattr(pet, "breed", None), 80),
        "sex": _clean(getattr(pet, "sex", None), 40),
        "age": _clean(_age_text(pet, today), 60),
        "birth": pet.birth_date.strftime("%d.%m.%Y") if getattr(pet, "birth_date", None) else "",
        "weight": f"{pet.weight_kg}" if getattr(pet, "weight_kg", None) else "",
        "allergies": [_clean(a, 80) for a in (getattr(pet, "allergies", None) or [])],
        "chronic": [_clean(c, 80) for c in (getattr(pet, "chronic_conditions", None) or [])],
        "notes": _clean(getattr(pet, "health_notes", None), 1200),
        "schedule": [
            {"kind": k, "done": cur[k].done_at, "due": cur[k].next_due_at}
            for k in KINDS
            if k in cur
        ],
        "history": [{"kind": e.kind, "done": e.done_at, "due": e.next_due_at} for e in history],
        "facts": [_clean(f, 200) for f in facts[:MAX_FACTS]],
        "generated": today,
    }


def _fmt(d: date) -> str:
    return d.strftime("%d.%m.%Y")


def generate_passport_pdf(data: dict, lang: str = "ru") -> bytes:
    lang = normalize_locale(lang)

    def L(key: str, **kw: Any) -> str:  # noqa: N802
        return t(f"pdf.passport.{key}", lang, **kw)

    def kind_label(kind: str) -> str:
        return t(f"health.kind.{kind}", lang)

    pdf = FPDF()
    pdf.add_font("DejaVu", "", str(_ASSETS / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(_ASSETS / "DejaVuSans-Bold.ttf"))
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    def line(text: str, size: int = 11, bold: bool = False, color=(40, 40, 40), h: float = 6.5):
        pdf.set_font("DejaVu", "B" if bold else "", size)
        pdf.set_text_color(*color)
        pdf.multi_cell(0, h, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def section(title: str):
        pdf.ln(3)
        pdf.set_font("DejaVu", "B", 12)
        pdf.set_fill_color(237, 232, 255)
        pdf.set_text_color(60, 40, 160)
        pdf.cell(0, 8, "  " + title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        pdf.ln(1)

    pdf.set_font("DejaVu", "B", 20)
    pdf.set_text_color(80, 60, 200)
    pdf.cell(0, 12, L("title"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    line(data["name"], 16, True, h=8)

    section(L("profile"))
    rows = [
        (L("breed"), data["breed"]),
        (L("sex"), data["sex"]),
        (L("age"), data["age"]),
        (L("birth"), data["birth"]),
        (L("weight"), f"{data['weight']} {L('kg')}" if data["weight"] else ""),
    ]
    for label, value in rows:
        if value:
            line(f"{label}: {value}")

    section(L("health"))
    line(f"{L('allergies')}: " + (", ".join(data["allergies"]) or "—"))
    line(f"{L('chronic')}: " + (", ".join(data["chronic"]) or "—"))
    if data["notes"]:
        line(f"{L('notes')}: {data['notes']}")

    section(L("schedule"))
    if data["schedule"]:
        for r in data["schedule"]:
            line(
                f"{kind_label(r['kind'])}: {L('last')} {_fmt(r['done'])} · "
                f"{L('next')} {_fmt(r['due'])}"
            )
    else:
        line("—")

    if data["history"]:
        section(L("history"))
        for r in data["history"]:
            line(f"{_fmt(r['done'])} — {kind_label(r['kind'])}", size=10, h=5.5)

    if data["facts"]:
        section(L("facts"))
        for f in data["facts"]:
            line(f"• {f}", size=10, h=5.5)

    pdf.ln(4)
    line(L("disclaimer", date=_fmt(data["generated"])), size=8, color=(140, 140, 140), h=4.5)
    return bytes(pdf.output())
