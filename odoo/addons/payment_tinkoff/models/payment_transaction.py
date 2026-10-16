import logging

from odoo import _, api, models
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_tinkoff import const
from odoo.addons.payment_tinkoff.controllers.main import TinkoffController
from odoo.exceptions import ValidationError
from odoo.tools import urls

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    @api.model
    def _compute_reference(self, provider_code, prefix=None, separator="-", **kwargs):
        if provider_code == "tinkoff":
            prefix = payment_utils.singularize_reference_prefix(prefix=prefix, separator=separator)
        return super()._compute_reference(
            provider_code, prefix=prefix, separator=separator, **kwargs
        )

    def _get_specific_rendering_values(self, processing_values):
        """Initiate Tinkoff payment (Init) and return PaymentURL for redirect form."""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != "tinkoff":
            return res

        base_url = self.provider_id.get_base_url()
        amount_kopecks = payment_utils.to_minor_currency_units(self.amount, self.currency_id)

        payload = {
            "Amount": int(amount_kopecks),
            "OrderId": self.reference,
            "Description": (self.reference or "Pepito order")[:250],
            "SuccessURL": urls.urljoin(base_url, TinkoffController._return_url),
            "FailURL": urls.urljoin(base_url, TinkoffController._return_url),
            "NotificationURL": urls.urljoin(base_url, TinkoffController._webhook_url),
            "DATA": {
                "Email": self.partner_email or "",
                "Phone": (self.partner_phone or "")[:20],
            },
        }

        if self.provider_id.tinkoff_send_receipt:
            receipt = self._tinkoff_prepare_receipt(amount_kopecks)
            if receipt:
                payload["Receipt"] = receipt

        try:
            init_data = self.provider_id._tinkoff_request("Init", payload)
        except ValidationError as error:
            self._set_error(str(error))
            return res

        payment_id = init_data.get("PaymentId")
        payment_url = init_data.get("PaymentURL")
        if not payment_url:
            self._set_error(_("Т-Банк не вернул PaymentURL."))
            return res

        self.provider_reference = str(payment_id) if payment_id else self.provider_reference
        return {"api_url": payment_url}

    def _tinkoff_prepare_receipt(self, amount_kopecks):
        """Minimal 54-FZ receipt payload for Init."""
        self.ensure_one()
        email = self.partner_email or self.company_id.email
        phone = self.partner_phone
        if not email and not phone:
            # Receipt requires Email or Phone
            email = "order@pepitopet.ru"

        items = [
            {
                "Name": (self.reference or "Заказ")[:128],
                "Price": int(amount_kopecks),
                "Quantity": 1.0,
                "Amount": int(amount_kopecks),
                "Tax": "none",
                "PaymentMethod": "full_prepayment",
                "PaymentObject": "commodity",
            }
        ]
        return {
            "Email": email or "",
            "Phone": (phone or "")[:64],
            "Taxation": self.provider_id.tinkoff_taxation or "usn_income",
            "Items": items,
        }

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        if provider_code != "tinkoff":
            return super()._extract_reference(provider_code, payment_data)
        # Notification / return: OrderId is our reference
        return payment_data.get("OrderId") or payment_data.get("orderId")

    def _extract_amount_data(self, payment_data):
        if self.provider_code != "tinkoff":
            return super()._extract_amount_data(payment_data)
        amount = payment_utils.to_major_currency_units(
            float(payment_data.get("Amount") or 0), self.currency_id
        )
        return {
            "amount": amount,
            "currency_code": "RUB",
        }

    def _apply_updates(self, payment_data):
        if self.provider_code != "tinkoff":
            super()._apply_updates(payment_data)
            return

        payment_id = payment_data.get("PaymentId") or payment_data.get("Paymentid")
        if payment_id:
            self.provider_reference = str(payment_id)

        status = (payment_data.get("Status") or payment_data.get("status") or "").upper()
        if not status:
            self._set_error(_("Нет Status в ответе Т-Банка."))
            return

        if status in const.PAYMENT_STATUS_MAPPING["done"]:
            self._set_done()
        elif status in const.PAYMENT_STATUS_MAPPING["pending"]:
            self._set_pending()
        elif status in const.PAYMENT_STATUS_MAPPING["cancel"]:
            self._set_canceled(state_message=status)
        else:
            _logger.info("Tinkoff unknown status %s for %s", status, self.reference)
            self._set_error(_("Неизвестный статус Т-Банка: %s") % status)
