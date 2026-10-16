"""Agent logic layer: declarative rules, structured AI IO, model cascade, tracing.

Business decisions (limits, pricing, referral tiers, model routing) live in
``rules.json`` — not in prompts and not scattered as magic numbers.
"""

from app.logic.cascade import ModelCascade
from app.logic.rules import get_rules, reload_rules

__all__ = ["ModelCascade", "get_rules", "reload_rules"]
