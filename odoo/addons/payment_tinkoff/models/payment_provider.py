import hashlib
import json
import logging

import requests
from odoo import _, fields, models
from odoo.addons.payment_tinkoff import const
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[("tinkoff", "T-Bank (Tinkoff)")],
        ondelete={"tinkoff": "set default"},
    )
    tinkoff_terminal_key = fields.Char(
        string="TerminalKey",
        help="Ключ терминала из ЛК интернет-эквайринга Т-Банка.",
        copy=False,
    )
    tinkoff_password = fields.Char(
        string="Password",
        help="Пароль терминала (для подписи Token).",
        copy=False,
        groups="base.group_system",
    )
    tinkoff_taxation = fields.Selection(
        selection=const.TAXATION_CODES,
        string="Система налогообложения (54-ФЗ)",
        default="usn_income",
        help="Передаётся в Receipt при Init, если включена онлайн-касса.",
    )
    tinkoff_send_receipt = fields.Boolean(
        string="Передавать чек (Receipt) в Init",
        default=True,
        help="Нужно при подключённой онлайн-кассе. Отключите для тестового терминала без кассы.",
    )

    # === FEATURES === #

    def _compute_feature_support_fields(self):
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == "tinkoff").update(
            {
                "support_refund": "full_only",
                "support_tokenization": False,
                "support_manual_capture": False,
                "support_express_checkout": False,
            }
        )

    def _get_supported_currencies(self):
        supported = super()._get_supported_currencies()
        if self.code == "tinkoff":
            supported = supported.filtered(lambda c: c.name in const.SUPPORTED_CURRENCIES)
        return supported

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        if self.code != "tinkoff":
            return super()._get_default_payment_method_codes()
        return const.DEFAULT_PAYMENT_METHOD_CODES

    # === TOKEN / API === #

    def _tinkoff_make_token(self, payload):
        """Build Tinkoff Token = SHA256 of sorted root scalar values + Password."""
        self.ensure_one()
        data = {}
        for key, value in payload.items():
            if key in ("Token", "DATA", "Receipt", "Shops", "Receipts"):
                continue
            if isinstance(value, (dict, list)):
                continue
            if value is None:
                continue
            if isinstance(value, bool):
                data[key] = "true" if value else "false"
            else:
                data[key] = value
        data["Password"] = self.tinkoff_password or ""
        concat = "".join(str(data[k]) for k in sorted(data.keys()))
        return hashlib.sha256(concat.encode("utf-8")).hexdigest()

    def _tinkoff_api_url(self, method):
        return f"{const.API_URL.rstrip('/')}/{method}"

    def _tinkoff_request(self, method, payload):
        """POST JSON to Tinkoff API with Token signature. Returns parsed dict."""
        self.ensure_one()
        if not self.tinkoff_terminal_key or not self.tinkoff_password:
            raise ValidationError(_("Заполните TerminalKey и Password Т-Банка."))

        body = dict(payload)
        body["TerminalKey"] = self.tinkoff_terminal_key
        body["Token"] = self._tinkoff_make_token(body)

        url = self._tinkoff_api_url(method)
        _logger.info("Tinkoff %s request OrderId=%s", method, body.get("OrderId"))
        try:
            resp = requests.post(
                url,
                data=json.dumps(body),
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as exc:
            _logger.exception("Tinkoff API error: %s", exc)
            raise ValidationError(_("Ошибка связи с Т-Банком: %s") % exc) from exc

        if not data.get("Success"):
            msg = data.get("Message") or data.get("Details") or data.get("ErrorCode") or data
            _logger.warning("Tinkoff %s failed: %s", method, data)
            raise ValidationError(_("Т-Банк отклонил запрос: %s") % msg)
        return data
