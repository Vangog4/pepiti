{
    'name': 'Pepito Design',
    'version': '1.0',
    'summary': 'Дизайн и контентные фиксы сайта pepitopet.ru',
    'category': 'Website',
    'depends': ['website', 'website_sale'],
    'data': [
        'views/homepage_fix.xml',
        'views/footer_fix.xml',
        'views/shop_fix.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pepito_design/static/src/scss/pepito_design.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
}
