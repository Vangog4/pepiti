"""Unit tests for AiService._postprocess — safe text normalization."""
import pytest
from app.services.ai_service import AiService

pp = AiService._postprocess


class TestPassthrough:
    def test_already_valid_html_unchanged(self):
        text = "<b>Главная причина:</b> Собака тянет поводок.\n\n<i>Совет:</i> Останавливайся."
        assert pp(text) == text.strip()

    def test_valid_html_with_code_unchanged(self):
        text = "<b>Команда</b>: <code>/start</code>\n\nЗапускает бота."
        assert pp(text) == text.strip()

    def test_empty_string(self):
        assert pp("") == ""

    def test_short_plain_text_no_injection(self):
        # Under 300 chars — no paragraph injection even with list markers
        text = "Короткий текст.\n1. Шаг один.\n2. Шаг два."
        assert "\n\n" not in pp(text)

    def test_markdown_asterisks_not_converted(self):
        # We do NOT convert markdown → HTML
        text = "**жирный** и *курсив* — остаются как есть."
        result = pp(text)
        assert "**жирный**" in result
        assert "<b>" not in result


class TestLineEndingNormalization:
    def test_crlf_to_lf(self):
        text = "Строка 1\r\nСтрока 2\r\nСтрока 3"
        assert "\r" not in pp(text)
        assert pp(text) == "Строка 1\nСтрока 2\nСтрока 3"

    def test_triple_newlines_collapsed(self):
        text = "Первый абзац.\n\n\n\nВторой абзац."
        result = pp(text)
        assert "\n\n\n" not in result
        assert "Первый абзац." in result
        assert "Второй абзац." in result

    def test_trailing_spaces_stripped_per_line(self):
        text = "Строка с пробелами   \nВторая строка  "
        result = pp(text)
        for line in result.split("\n"):
            assert not line.endswith(" ")


class TestUnsupportedTagReplacement:
    def test_strong_replaced_with_b(self):
        text = "<strong>Важно</strong> запомнить это."
        result = pp(text)
        assert "<b>Важно</b>" in result
        assert "<strong>" not in result
        assert "</strong>" not in result

    def test_em_replaced_with_i(self):
        text = "Это <em>курсив</em> в тексте."
        result = pp(text)
        assert "<i>курсив</i>" in result
        assert "<em>" not in result

    def test_br_self_closing_replaced_with_newline(self):
        result = pp("Строка 1<br/>Строка 2")
        assert "\n" in result
        assert "<br" not in result

    def test_br_open_replaced_with_newline(self):
        result = pp("Строка 1<br>Строка 2")
        assert "\n" in result
        assert "<br>" not in result

    def test_h_tags_stripped_text_preserved(self):
        text = "<h2>Заголовок раздела</h2>\nТекст раздела."
        result = pp(text)
        assert "Заголовок раздела" in result
        assert "<h2>" not in result
        assert "</h2>" not in result

    def test_h1_through_h6_all_stripped(self):
        for n in range(1, 7):
            text = f"<h{n}>Текст</h{n}>"
            result = pp(text)
            assert "Текст" in result
            assert f"<h{n}>" not in result

    def test_valid_b_i_code_untouched(self):
        text = "<b>жирный</b> и <i>курсив</i> и <code>код</code>"
        result = pp(text)
        assert "<b>жирный</b>" in result
        assert "<i>курсив</i>" in result
        assert "<code>код</code>" in result


class TestLayerBCD:
    """Regression tests for Layers B (whitelist), C (& escape), D (fallback)."""

    # — Layer B-2: list/block tags —

    def test_ul_li_converted_to_bullets(self):
        text = "<ul><li>Пункт A</li><li>Пункт B</li></ul>"
        result = pp(text)
        assert "• Пункт A" in result
        assert "• Пункт B" in result
        assert "<ul>" not in result
        assert "<li>" not in result

    def test_p_and_div_tags_stripped(self):
        text = "<p>Первый абзац</p><div>Второй блок</div>"
        result = pp(text)
        assert "Первый абзац" in result
        assert "Второй блок" in result
        assert "<p>" not in result
        assert "<div>" not in result

    # — Layer B-3: unknown-tag stripping —

    def test_span_tag_stripped_content_kept(self):
        text = '<span class="highlight">Важный текст</span>'
        result = pp(text)
        assert "Важный текст" in result
        assert "<span" not in result
        assert "</span>" not in result

    # — Layer C: bare & escape —

    def test_bare_ampersand_escaped(self):
        result = pp("Tom & Jerry дрессируют вместе")
        assert "&amp;" in result
        assert "Tom &amp; Jerry" in result

    def test_already_escaped_amp_not_double_escaped(self):
        result = pp("Пример &amp; ещё одно &lt;значение&gt;")
        assert "&&" not in result
        assert "&amp;amp;" not in result
        assert "&amp;" in result
        assert "&lt;" in result

    # — Layer C-pre: bare < escape —

    def test_bare_lt_in_text_escaped(self):
        result = pp("Размер < 10 кг — маленькая порода")
        assert "&lt;" in result
        assert "Размер &lt; 10 кг" in result

    def test_valid_tags_not_escaped_by_lt_rule(self):
        text = "<b>Жирный</b> и <i>курсив</i>"
        result = pp(text)
        assert "<b>Жирный</b>" in result
        assert "<i>курсив</i>" in result
        assert "&lt;b&gt;" not in result

    # — Layer D: unclosed-tag fallback —

    def test_unclosed_b_tag_falls_back_to_plain(self):
        result = pp("<b>Незакрытый тег — текст продолжается")
        assert "<b>" not in result
        assert "Незакрытый тег" in result

    def test_balanced_tags_not_stripped_by_fallback(self):
        text = "<b>Правильно закрытый</b> тег"
        result = pp(text)
        assert "<b>" in result
        assert "</b>" in result


class TestParagraphInjection:
    def _long_preamble(self, n=300):
        return "А" * n + ".\n"

    def test_injection_for_long_text_with_numbered_list(self):
        text = self._long_preamble() + "1. Первый шаг.\n2. Второй шаг.\n3. Третий шаг."
        result = pp(text)
        assert "\n\n" in result

    def test_injection_for_long_text_with_dash_list(self):
        text = self._long_preamble() + "- Пункт A.\n- Пункт B.\n- Пункт C."
        result = pp(text)
        assert "\n\n" in result

    def test_injection_for_long_text_with_bullet(self):
        text = self._long_preamble() + "• Пункт A.\n• Пункт B."
        result = pp(text)
        assert "\n\n" in result

    def test_no_injection_when_already_has_double_newline(self):
        text = self._long_preamble() + "\n\n1. Шаг один.\n2. Шаг два."
        result = pp(text)
        # \n\n was already present, injection not triggered; count should be same
        assert result.count("\n\n") == text.strip().count("\n\n")

    def test_no_injection_for_short_text_with_markers(self):
        text = "Текст.\n1. Шаг один.\n2. Шаг два."
        assert len(text) < 300
        assert "\n\n" not in pp(text)
