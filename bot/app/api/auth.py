import hashlib
import hmac
import json
from urllib.parse import parse_qsl


def validate_init_data(init_data: str, bot_token: str) -> dict | None:
    """Validate Telegram WebApp initData via HMAC-SHA256.

    Returns parsed data dict (with 'user' as dict) on success, None on failure.
    """
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    hash_value = params.pop("hash", None)
    if not hash_value:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, hash_value):
        return None

    user_json = params.get("user")
    if user_json:
        try:
            params["user"] = json.loads(user_json)
        except json.JSONDecodeError:
            return None

    return params
