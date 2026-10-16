import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

# Telegram recommends rejecting initData older than ~24h.
_MAX_AUTH_AGE_SEC = 24 * 60 * 60


def validate_init_data(
    init_data: str, bot_token: str, *, max_age_sec: int = _MAX_AUTH_AGE_SEC
) -> dict | None:
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

    try:
        auth_date = int(params.get("auth_date") or 0)
    except (TypeError, ValueError):
        return None
    if auth_date <= 0 or abs(time.time() - auth_date) > max_age_sec:
        return None

    user_json = params.get("user")
    if isinstance(user_json, str):
        try:
            params["user"] = json.loads(user_json)
        except json.JSONDecodeError:
            return None

    return params
