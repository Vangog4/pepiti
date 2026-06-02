"""
PDF export service for Pepito training plans.

Requires fpdf2 (uv add fpdf2) and DejaVu fonts in app/assets/:
  DejaVuSans.ttf
  DejaVuSans-Bold.ttf
"""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

_ASSETS = Path(__file__).parent.parent / "assets"
_FONT_REGULAR = str(_ASSETS / "DejaVuSans.ttf")
_FONT_BOLD = str(_ASSETS / "DejaVuSans-Bold.ttf")

_DAY_NAMES = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}


def generate_training_pdf(
    pet_name: str,
    plan_title: str,
    plan_goal: str,
    tasks: list[dict],
) -> bytes:
    """
    Generate a PDF training plan and return the raw bytes.

    ``tasks`` is a list of dicts with keys:
      - day_of_week (int 1–7)
      - title (str)
      - description (str | None)
      - duration_minutes (int | None)
      - difficulty (str | None)
      - is_completed (bool)
    """
    pdf = FPDF()
    pdf.add_font("DejaVu", "", _FONT_REGULAR)
    pdf.add_font("DejaVu", "B", _FONT_BOLD)

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Header ────────────────────────────────────────────────────────────
    pdf.set_font("DejaVu", "B", 20)
    pdf.set_text_color(80, 60, 200)
    pdf.cell(0, 12, "Pepito — план тренировок", ln=True, align="C")

    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, f"Питомец: {pet_name}", ln=True, align="C")

    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, plan_title, ln=True, align="C")

    if plan_goal:
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, f"Цель: {plan_goal}", ln=True, align="C")

    # ── Divider ───────────────────────────────────────────────────────────
    pdf.set_draw_color(180, 160, 240)
    pdf.set_line_width(0.5)
    pdf.ln(3)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(5)

    # ── Group tasks by day ────────────────────────────────────────────────
    by_day: dict[int, list[dict]] = {}
    for task in tasks:
        dow = task.get("day_of_week") or 0
        by_day.setdefault(dow, []).append(task)

    for day_num in sorted(by_day.keys()):
        day_tasks = by_day[day_num]
        day_label = _DAY_NAMES.get(day_num, f"День {day_num}")

        # Day header
        pdf.set_font("DejaVu", "B", 12)
        pdf.set_fill_color(237, 232, 255)
        pdf.set_text_color(60, 40, 160)
        pdf.cell(0, 9, f"  {day_label}", ln=True, fill=True)
        pdf.ln(2)

        for task in day_tasks:
            title = task.get("title") or ""
            description = task.get("description") or ""
            duration = task.get("duration_minutes")
            difficulty = task.get("difficulty") or ""
            done = task.get("is_completed", False)

            # Task title with done indicator
            done_mark = "✓ " if done else "○ "
            pdf.set_font("DejaVu", "B", 11)
            pdf.set_text_color(30, 30, 30)
            title_line = f"{done_mark}{title}"
            pdf.cell(0, 8, title_line, ln=True)

            # Meta: duration + difficulty
            meta_parts = []
            if duration:
                meta_parts.append(f"{duration} мин")
            if difficulty:
                meta_parts.append(difficulty)
            if meta_parts:
                pdf.set_font("DejaVu", "", 9)
                pdf.set_text_color(130, 130, 130)
                pdf.cell(0, 5, "   " + " · ".join(meta_parts), ln=True)

            # Description
            if description:
                pdf.set_font("DejaVu", "", 10)
                pdf.set_text_color(70, 70, 70)
                pdf.multi_cell(0, 5.5, "   " + description)

            pdf.ln(3)

        pdf.ln(4)

    # ── Footer ────────────────────────────────────────────────────────────
    pdf.set_y(-18)
    pdf.set_font("DejaVu", "", 8)
    pdf.set_text_color(180, 180, 180)
    pdf.cell(0, 5, "Сгенерировано Pepito · AI-кинолог для собак · @pepitopetbot", align="C")

    return bytes(pdf.output())
