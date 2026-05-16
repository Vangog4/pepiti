_BASE = "https://pepitopet.ru/shop"
_UTM = "utm_source=pepito_bot&utm_medium=telegram"


def _url(tags: str, campaign: str) -> str:
    prefix = f"?{tags}&" if tags else "?"
    return f"{_BASE}{prefix}{_UTM}&utm_campaign={campaign}"


# Тег-фильтры Odoo: /shop?tags=<id>
# id=2 Для дрессировки, id=3 Долгоиграющее, id=7 Для мелких пород, id=10 Для щенков
SHOP_URL_TRAINING  = _url("tags=2",          "training_treats")   # Для дрессировки
SHOP_URL_LONGPLAY  = _url("tags=3",          "longplay")           # Долгоиграющее
SHOP_URL_BY_SIZE   = _url("tags=7&tags=10",  "by_size")            # Мелкие породы + Щенки
SHOP_URL_MAIN      = _url("",               "shop_menu")           # Весь каталог
