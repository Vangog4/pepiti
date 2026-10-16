import json
import logging
import pprint

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TinkoffController(http.Controller):
    _return_url = "/payment/tinkoff/return"
    _webhook_url = "/payment/tinkoff/notification"

    @http.route(
        _return_url,
        type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,
        save_session=False,
    )
    def tinkoff_return_from_checkout(self, **data):
        """Customer browser returns from T-Bank payment page."""
        _logger.info("Tinkoff return data:\n%s", pprint.pformat(data))
        # Prefer OrderId from query; fall back to session-less status page
        tx_sudo = request.env["payment.transaction"].sudo()._search_by_reference("tinkoff", data)
        if tx_sudo:
            # Optionally refresh status from API
            try:
                if tx_sudo.provider_reference:
                    status_data = tx_sudo.provider_id._tinkoff_request(
                        "GetState",
                        {"PaymentId": int(tx_sudo.provider_reference)},
                    )
                    # Merge OrderId for reference search consistency
                    status_data.setdefault("OrderId", tx_sudo.reference)
                    tx_sudo._process("tinkoff", status_data)
            except Exception:
                _logger.exception("Tinkoff GetState on return failed for %s", tx_sudo.reference)
        return request.redirect("/payment/status")

    @http.route(
        _webhook_url,
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
        save_session=False,
    )
    def tinkoff_notification(self, **kwargs):
        """Server-to-server notification. Must respond with plain text OK."""
        raw = request.httprequest.get_data(as_text=True) or ""
        try:
            data = json.loads(raw) if raw.strip().startswith("{") else dict(kwargs)
        except json.JSONDecodeError:
            data = dict(kwargs)
            if raw:
                _logger.warning("Tinkoff notification non-JSON body: %s", raw[:500])

        _logger.info("Tinkoff notification:\n%s", pprint.pformat(data))

        tx_sudo = request.env["payment.transaction"].sudo()._search_by_reference("tinkoff", data)
        if not tx_sudo:
            _logger.warning(
                "Tinkoff notification: transaction not found for %s", data.get("OrderId")
            )
            # Still OK so Tinkoff does not retry forever on cancelled/unknown orders
            return request.make_response("OK", headers=[("Content-Type", "text/plain")])

        # Verify Token if present
        if not self._verify_token(data, tx_sudo.provider_id):
            _logger.warning("Tinkoff notification: invalid Token for %s", tx_sudo.reference)
            return request.make_response(
                "ERROR", status=403, headers=[("Content-Type", "text/plain")]
            )

        tx_sudo._process("tinkoff", data)
        return request.make_response("OK", headers=[("Content-Type", "text/plain")])

    @staticmethod
    def _verify_token(data, provider):
        """Validate notification Token against Password."""
        received = data.get("Token")
        if not received or not provider.tinkoff_password:
            # Some sandbox paths omit Token — log and accept only in test mode
            return provider.state == "test"
        expected = provider._tinkoff_make_token(data)
        return received.lower() == expected.lower()
