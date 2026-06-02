"""
Lightweight i18n engine.

Key design decisions:
- No external dependencies — pure stdlib
- Per-locale files in app/i18n/locales/<code>.py, each exports STRINGS dict
- Lazy loading + module-level cache (one import per locale per process)
- Namespace keys: "menu.main.title", "settings.reminders.on", etc.
- Fallback chains: uk→ru, et→en→ru; any unknown→ru
- _SafeDict interpolation: missing kwargs leave the placeholder intact
- Slavic plural rules for ru/uk; simple en rules for everything else
"""

import importlib
import re
from typing import Any

DEFAULT_LOCALE = "ru"
SUPPORTED_LOCALES = frozenset({"ru", "en", "de", "fr", "es", "pt"})

# Fallback chain per locale: first match wins
_FALLBACK_CHAINS: dict[str, tuple[str, ...]] = {
    "ru": ("ru",),
    "en": ("en", "ru"),
    "de": ("de", "en", "ru"),
    "fr": ("fr", "en", "ru"),
    "es": ("es", "en", "ru"),
    "pt": ("pt", "en", "ru"),
}

# Telegram language_code values → canonical locale
_LOCALE_ALIASES: dict[str, str] = {
    "ru": "ru",
    "ru-RU": "ru",
    "ru_RU": "ru",
    "be": "ru",  # Belarusian → Russian fallback
    "uk": "ru",  # Ukrainian → Russian fallback (uk locale removed)
    "en": "en",
    "en-US": "en",
    "en_US": "en",
    "en-GB": "en",
    "en-AU": "en",
    "en-CA": "en",
    "de": "de",
    "de-DE": "de",
    "de_DE": "de",
    "de-AT": "de",
    "de-CH": "de",
    "fr": "fr",
    "fr-FR": "fr",
    "fr_FR": "fr",
    "fr-BE": "fr",
    "fr-CA": "fr",
    "es": "es",
    "es-ES": "es",
    "es_ES": "es",
    "es-MX": "es",
    "es-419": "es",
    "pt": "pt",
    "pt-BR": "pt",
    "pt_BR": "pt",
    "pt-PT": "pt",
    "pt_PT": "pt",
}

_LOCALE_CACHE: dict[str, dict[str, str]] = {}


class _SafeDict(dict):
    """dict that returns '{key}' for missing keys instead of raising KeyError."""

    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def normalize_locale(lang_code: str | None) -> str:
    """Map any Telegram language_code to a supported locale (default: 'ru')."""
    if not lang_code:
        return DEFAULT_LOCALE
    code = lang_code.strip()
    if code in _LOCALE_ALIASES:
        return _LOCALE_ALIASES[code]
    base = re.split(r"[-_]", code)[0].lower()
    return _LOCALE_ALIASES.get(base, DEFAULT_LOCALE)


def _load_locale(locale: str) -> dict[str, str]:
    if locale not in _LOCALE_CACHE:
        try:
            mod = importlib.import_module(f"app.i18n.locales.{locale}")
            _LOCALE_CACHE[locale] = getattr(mod, "STRINGS", {})
        except ImportError:
            _LOCALE_CACHE[locale] = {}
    return _LOCALE_CACHE[locale]


def t(key: str, lang: str = DEFAULT_LOCALE, **kwargs: Any) -> str:
    """
    Translate key to lang with optional interpolation.

    Example:
        t("menu.main.streak", "en", emoji="🔥", n=5, days="days")
        → "🔥 Streak: <b>5 days</b> in a row\\n\\n"

    Falls back through _FALLBACK_CHAINS; ultimate fallback is the key itself.
    Missing interpolation kwargs leave the placeholder intact (via _SafeDict).
    """
    locale = normalize_locale(lang)
    chain = _FALLBACK_CHAINS.get(locale, (locale, DEFAULT_LOCALE))
    for loc in chain:
        value = _load_locale(loc).get(key)
        if value is not None:
            return value.format_map(_SafeDict(kwargs)) if kwargs else value
    return key  # last resort: return the key name


def pluralize(n: int, lang: str = DEFAULT_LOCALE, **forms: str) -> str:
    """
    Return the correct plural form for n in lang.

    Slavic (ru, uk): pass one=, few=, many=
    English / other: pass one=, other=  (few= ignored)

    Example (ru): pluralize(3, "ru", one="день", few="дня", many="дней") → "дня"
    Example (en): pluralize(3, "en", one="day", other="days") → "days"
    """
    locale = normalize_locale(lang)
    if locale in ("ru", "uk"):
        mod10, mod100 = abs(n) % 10, abs(n) % 100
        if 11 <= mod100 <= 19:
            return forms.get("many", forms.get("other", ""))
        if mod10 == 1:
            return forms.get("one", "")
        if 2 <= mod10 <= 4:
            return forms.get("few", forms.get("other", ""))
        return forms.get("many", forms.get("other", ""))
    else:
        return forms.get("one", "") if n == 1 else forms.get("other", forms.get("many", ""))
