"""P1.7: 1080x1920 story cards rendered at 2x without a browser."""

import struct
import xml.etree.ElementTree as ET

import pytest

from app.cards.render import (
    CARD_H,
    CARD_W,
    SCALE,
    build_svg,
    fit_size,
    render_card,
    strip_unrenderable,
    wrap_text,
)


def png_size(png: bytes) -> tuple[int, int]:
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", png[16:24])


def test_wrap_respects_width_and_splits_long_words():
    lines = wrap_text("Рекс не пропускает тренировки уже две недели подряд", 18)
    assert all(len(line) <= 18 for line in lines) and " ".join(lines).count("Рекс") == 1
    hard = wrap_text("Супердлинноеслововбезпробелов", 10)
    assert (
        all(len(line) <= 10 for line in hard) and "".join(hard) == "Супердлинноеслововбезпробелов"
    )
    assert wrap_text("", 10) == []


def test_wrap_caps_line_count_with_ellipsis():
    lines = wrap_text("слово " * 60, 12, max_lines=3)
    assert len(lines) == 3 and lines[-1].endswith("…")


def test_strip_unrenderable_removes_emoji_keeps_text():
    assert strip_unrenderable("🔥7 дней ⭐ Premium 🏆") == "7 дней Premium"
    assert strip_unrenderable("Рекс‍️") == "Рекс"
    assert strip_unrenderable("Zoë — café") == "Zoë — café"


def test_fit_size_shrinks_for_long_text_but_has_a_floor():
    assert fit_size(["Рекс"], 920, base=96, min_size=56) == 96
    long = fit_size(["x" * 30], 920, base=96, min_size=56)
    assert 56 <= long < 96
    assert fit_size(["x" * 400], 920, base=96, min_size=56) == 56


DATA = {
    "streak": dict(big="12", caption="дней подряд", headline="Рекс не пропускает тренировки"),
    "badge": dict(big="7", caption="Новая ачивка", headline="7 дней подряд"),
    "week": dict(
        big="5",
        caption="Итоги недели",
        headline="Рекс",
        rows=[("Тренировок", "5"), ("Прогулок", "3"), ("Минут", "90")],
    ),
    "passport": dict(
        big="Рекс",
        caption="Паспорт",
        headline="Лабрадор",
        rows=[("Возраст", "2 г"), ("Вес", "28,5 кг")],
    ),
}


@pytest.mark.parametrize("kind", list(DATA))
def test_svg_is_well_formed_and_escapes_user_text(kind):
    data = dict(DATA[kind], headline='<script>alert(1)</script> & "Рекс"')
    svg = build_svg(kind, data)
    ET.fromstring(svg)  # raises if malformed
    assert "<script>" not in svg and "&lt;script&gt;" in svg


def test_unknown_kind_is_rejected():
    with pytest.raises(ValueError):
        build_svg("nope", DATA["streak"])


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", list(DATA))
async def test_render_gives_2x_png(kind):
    png = await render_card(kind, DATA[kind])
    assert png_size(png) == (int(CARD_W * SCALE), int(CARD_H * SCALE))
    assert 5_000 < len(png) < 3_000_000


@pytest.mark.asyncio
async def test_hostile_input_still_renders():
    hostile = dict(
        big="🔥" * 40,
        caption="а" * 300,
        headline="</text><rect/>" * 20 + "🏆" * 50,
        rows=[("x" * 200, "y" * 200)] * 8,
    )
    png = await render_card("week", hostile)
    assert png_size(png) == (int(CARD_W * SCALE), int(CARD_H * SCALE))


# ── layout regressions found by looking at the rendered cards ───────────────


def test_ellipsize_never_cuts_mid_word_silently():
    from app.cards.render import ellipsize

    assert ellipsize("курица", 10) == "курица"
    out = ellipsize("курица, говядина, рыба", 12)
    assert len(out) <= 12 and out.endswith("…")
    assert ellipsize("", 5) == ""


def test_long_big_text_wraps_into_the_circle_instead_of_being_cut():
    svg = build_svg("passport", dict(big="Александр Македонский III", caption="x", headline="y"))
    # the full name survives (wrapped over lines), not truncated to 12 characters
    assert "Александр" in svg and "Македонский" in svg
    assert "Александр Ма<" not in svg


def test_row_values_use_ellipsis_not_hard_cut():
    svg = build_svg(
        "week",
        dict(
            big="1",
            caption="c",
            headline="h",
            rows=[("Allergien", "курица, говядина, рыба, пшеница")],
        ),
    )
    assert "…" in svg and "курица, говяди<" not in svg


def test_short_name_helper():
    from app.cards.data import short_name

    assert short_name("Рекс", 16) == "Рекс"
    assert (
        short_name("Александр Македонский III", 16) == "Александр Маке…"[:16]
        or len(short_name("Александр Македонский III", 16)) <= 16
    )
    assert len(short_name("Александр Македонский III", 16)) <= 16


def test_headline_keeps_the_message_for_long_pet_names():
    from app.cards.data import streak_card

    d = streak_card("Александр Македонский III", 12, "ru")
    assert "тренировки" in d["headline"]
    assert "…" not in " ".join(wrap_text(d["headline"], 18, max_lines=3)[-1:])
