"""Mobile authentication helpers: VK ID token verification and JWT utilities."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt


async def verify_vk_token(vk_access_token: str, vk_user_id: int) -> bool:
    """Call VK API to verify access token belongs to vk_user_id.

    Returns True if the token is valid and the user ID matches.
    """
    import aiohttp

    url = "https://api.vk.com/method/users.get"
    params = {
        "access_token": vk_access_token,
        "v": "5.199",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    return False
                data = await resp.json()
        response_list = data.get("response")
        if not response_list or not isinstance(response_list, list):
            return False
        user = response_list[0]
        return int(user.get("id", -1)) == int(vk_user_id)
    except Exception:
        return False


def issue_jwt(user_id: int, secret: str, expire_days: int) -> str:
    """Create a signed JWT with sub=user_id and expiry."""
    now = datetime.now(tz=UTC)
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(days=expire_days),
        "iat": now,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_jwt(token: str, secret: str) -> int | None:
    """Decode JWT and return user_id (sub claim) or None on any error."""
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        sub = payload.get("sub")
        if sub is None:
            return None
        return int(sub)
    except Exception:
        return None
