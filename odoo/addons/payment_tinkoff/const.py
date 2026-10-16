"""T-Bank (Tinkoff) Acquiring constants."""

# Production API base (test terminals use the same host with DEMO TerminalKey).
API_URL = "https://securepay.tinkoff.ru/v2/"

SUPPORTED_CURRENCIES = ["RUB"]

# Tinkoff payment Status → Odoo transaction state buckets
PAYMENT_STATUS_MAPPING = {
    "pending": [
        "NEW",
        "FORM_SHOWED",
        "AUTHORIZING",
        "3DS_CHECKING",
        "3DS_CHECKED",
        "PAY_CHECKING",
        "AUTHORIZED",  # authorized, capture pending
        "CONFIRMING",
    ],
    "done": [
        "CONFIRMED",
    ],
    "cancel": [
        "CANCELED",
        "DEADLINE_EXPIRED",
        "REJECTED",
        "REVERSED",
        "REFUNDED",
        "PARTIAL_REFUNDED",
        "AUTH_FAIL",
    ],
}

DEFAULT_PAYMENT_METHOD_CODES = {
    "card",
    "visa",
    "mastercard",
    "mir",
}

# 54-FZ taxation codes accepted by Init.Receipt.Taxation
TAXATION_CODES = [
    ("osn", "ОСН"),
    ("usn_income", "УСН доходы"),
    ("usn_income_outcome", "УСН доходы-расходы"),
    ("envd", "ЕНВД"),
    ("esn", "ЕСН"),
    ("patent", "Патент"),
]

# Map Odoo tax amount approx → Tinkoff Tax tag
# Used only if receipt is enabled.
TAX_MAP_DEFAULT = "none"  # none | vat0 | vat10 | vat20 | vat110 | vat120
