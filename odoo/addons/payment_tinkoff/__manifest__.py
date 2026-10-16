{
    "name": "Payment Provider: T-Bank (Tinkoff)",
    "version": "1.0.0",
    "category": "Accounting/Payment Providers",
    "summary": "Интернет-эквайринг Т-Банка (Тинькофф) для eCommerce",
    "description": """
Приём платежей на сайте через API интернет-эквайринга Т-Банка (Tinkoff Acquiring v2).

Нужны TerminalKey и Password из личного кабинета business.tbank.ru / oplata.
    """,
    "author": "Pepito",
    "license": "LGPL-3",
    "depends": ["payment", "website_payment"],
    "data": [
        "views/payment_tinkoff_templates.xml",
        "views/payment_provider_views.xml",
        "data/payment_method_data.xml",
        "data/payment_provider_data.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
}
