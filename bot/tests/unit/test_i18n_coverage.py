"""
i18n coverage guard — catches missing keys and broken placeholders before merge.
Run: pytest tests/unit/test_i18n_coverage.py -v
"""
import re
import sys

import pytest

sys.path.insert(0, ".")

from app.i18n.core import _load_locale

# Keys that must exist in ru.py (wired into handlers in this batch)
REQUIRED_KEYS = [
    "common.back_menu.btn",
    "common.back.btn",
    "common.menu.btn",
    "error.no_pet",
    "onboarding.start.returning",
    "onboarding.ai.welcome",
    "onboarding.ai.thinking",
    "onboarding.ai.photo_prompt",
    "onboarding.ai.clarify",
    "onboarding.ai.clarify.name",
    "onboarding.ai.clarify.breed",
    "onboarding.ai.clarify.age_category",
    "onboarding.done.welcome",
    "onboarding.done.referral_bonus",
    "onboarding.done.plan_loading",
    "onboarding.done.first_plan",
    "onboarding.done.fallback",
    "training.loading",
    "training.refresh.confirm",
    "training.refresh.confirm.yes",
    "training.refresh.confirm.no",
    "training.refresh.loading",
    "training.refresh.toast",
    "training.week.loading",
    "training.week.refresh.confirm",
    "training.week.refresh.loading",
    "training.week.empty",
    "training.week.empty.cta.btn",
    "training.explain.loading",
    "training.explain.back_daily.btn",
    "training.explain.back_weekly.btn",
    "training.plan.not_found",
    "training.done",
    "training.week_done",
    "training.share.text",
    "training.share.btn",
    "ai.fallback",
    "ai.rate_limit",
    "ai.rate_limit.btn",
    "ai.analyzing.premium",
    "ai.analyzing.free",
    "ai.progress.premium.header",
    "ai.progress.free.header",
    "ai.progress.back.btn",
    "ai.retry.btn",
    "ai.back_menu.btn",
    "coach.entry",
    "coach.thinking",
    "stats.header",
    "stats.days_with_us",
    "stats.completed",
    "stats.level",
    "stats.motivate",
    "stats.analysis.premium.btn",
    "stats.analysis.free.btn",
    "profile.header",
    "profile.breed",
    "profile.weight.unknown",
    "profile.issues.none",
    "profile.schedule.unknown",
    "profile.edit.btn",
    "shop.title",
    "shop.body",
    "shop.cat.training.btn",
    "invite.title",
    "invite.link_label",
    "invite.bonus",
    "invite.count",
    "invite.share.btn",
    "referral.notify.base",
    "referral.notify.milestone",
    "referral.notify.next_hint",
    "referral.notify.all_done",
    "premium.active.title",
    "premium.upsell.body",
    "premium.upsell.btn",
    "premium.activated",
    "premium.refunded",
    "reminder.title",
    "reminder.status.off",
    "reminder.status.on",
    "reminder.status.default",
    "reminder.input.prompt",
    "reminder.disabled",
    "reminder.saved",
    "reminder.error.format",
    "reminder.enable.btn",
    "reminder.change.btn",
    "reminder.disable.btn",
    "reminder.settings.btn",
    "reminder.menu.btn",
]


def test_required_keys_in_ru():
    """All keys wired into handlers must exist in ru.py."""
    ru = _load_locale("ru")
    missing = [k for k in REQUIRED_KEYS if k not in ru]
    assert not missing, f"Required keys missing from ru.py: {missing}"


def test_all_en_keys_in_ru():
    """Every key in en.py must also exist in ru.py (ru is the source of truth)."""
    ru = _load_locale("ru")
    en = _load_locale("en")
    orphan = [k for k in en if k not in ru]
    assert not orphan, f"Keys in en.py not in ru.py (orphan keys): {orphan}"


def test_no_positional_placeholders_in_ru():
    """ru.py strings must not use positional {} or {0} placeholders — only named."""
    ru = _load_locale("ru")
    bad: list[str] = []
    for key, val in ru.items():
        if re.search(r"\{(\d+)?\}", val):
            bad.append(f"{key!r}: {val[:60]!r}")
    assert not bad, f"Positional placeholders found in ru.py:\n" + "\n".join(bad)


def test_t_resolves_known_keys():
    """t() must return the translation, not echo the key, for known ru keys."""
    from app.i18n import t
    ru = _load_locale("ru")
    for key in list(ru.keys())[:10]:
        result = t(key, "ru")
        assert result != key, f"t({key!r}, 'ru') echoed the key — missing from locale?"


def test_t_fallback_unknown_locale():
    """t() must not raise for an unknown locale and must return the ru value."""
    from app.i18n import t
    ru = _load_locale("ru")
    result = t("menu.main.greeting", "xx_UNKNOWN_LOCALE")
    assert result == ru["menu.main.greeting"]


def test_en_key_count_reasonable():
    """en.py should have a substantial portion of ru.py keys (covers this batch)."""
    ru = _load_locale("ru")
    en = _load_locale("en")
    coverage = len(en) / len(ru) if ru else 0
    assert coverage >= 0.7, (
        f"en.py coverage too low: {len(en)}/{len(ru)} = {coverage:.0%}. "
        "Add missing EN translations."
    )
