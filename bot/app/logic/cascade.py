"""Model cascade: cheap → escalate on schema failure / hard tasks."""

from __future__ import annotations

from typing import Any


class ModelCascade:
    """Resolve Gemini model id by task kind and retry ladder."""

    def __init__(self, ai_rules: dict[str, Any] | None = None) -> None:
        if ai_rules is None:
            from app.logic.rules import get_rules

            ai_rules = get_rules().get("ai", {})
        self._ai = ai_rules
        models = ai_rules.get("models") or {}
        self.default = models.get("default", "gemini-2.5-flash-lite")
        self.escalate = models.get("escalate", "gemini-2.5-flash")
        self.media = models.get("media", self.escalate)
        self.premium = models.get("premium", self.escalate)
        self.schema_retries = int(ai_rules.get("schema_retries", 1))
        self._kinds: dict[str, str] = dict(ai_rules.get("kinds") or {})

    def tier_for(self, kind: str) -> str:
        return self._kinds.get(kind, "default")

    def model_for(self, kind: str) -> str:
        tier = self.tier_for(kind)
        return {
            "default": self.default,
            "escalate": self.escalate,
            "media": self.media,
            "premium": self.premium,
        }.get(tier, self.default)

    def ladder_for(self, kind: str) -> list[str]:
        """Ordered unique models: primary then escalate (if different).

        ``schema_retries`` is the number of *extra* attempts after the first,
        each preferably on a stronger model.
        """
        primary = self.model_for(kind)
        ladder = [primary]
        if self.schema_retries > 0 and self.escalate != primary:
            ladder.append(self.escalate)
        # de-dupe preserving order
        seen: set[str] = set()
        out: list[str] = []
        for m in ladder:
            if m not in seen:
                seen.add(m)
                out.append(m)
        return out
