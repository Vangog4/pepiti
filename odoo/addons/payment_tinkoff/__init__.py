from odoo.addons.payment import reset_payment_provider, setup_provider

from . import controllers, models

__all__ = ["controllers", "models", "post_init_hook", "uninstall_hook"]


def post_init_hook(env):
    setup_provider(env, "tinkoff")


def uninstall_hook(env):
    reset_payment_provider(env, "tinkoff")
