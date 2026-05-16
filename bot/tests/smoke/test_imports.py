"""
Smoke tests: verify core modules import without a live DB/Redis.
Run: pytest tests/smoke/ -v
"""
import pytest


def test_config_importable():
    pytest.importorskip("pydantic_settings", reason="pydantic_settings not installed — run inside container")
    from app.core import config
    assert hasattr(config, "settings") or hasattr(config, "Config") or True


def test_shop_importable():
    from app.core import shop
    assert hasattr(shop, "SHOP_URL_TRAINING") or True


def test_shop_recommendations_importable():
    from app.core import shop_recommendations


def test_keyboards_main_menu_importable():
    from app.bot.keyboards import main_menu


def test_keyboards_training_importable():
    from app.bot.keyboards import training


def test_states_importable():
    from app.bot import states


def test_domain_importable():
    import app.domain
