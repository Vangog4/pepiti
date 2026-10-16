{
    'name': 'Pepito Design',
    'version': '1.0',
    'summary': 'Дизайн и контентные фиксы сайта pepitopet.ru',
    'category': 'Website',
    'depends': ['website', 'website_sale', 'website_blog'],
    'data': [
        'views/homepage_fix.xml',
        'views/footer_fix.xml',
        'views/shop_fix.xml',
        'views/blog_seo.xml',
        'views/blog_ui.xml',
        'views/robots_seo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pepito_design/static/src/scss/pepito_design.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
}
