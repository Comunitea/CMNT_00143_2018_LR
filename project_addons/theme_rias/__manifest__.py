# -*- coding: utf-8 -*-
{
    'name': 'Las Rías Theme',
    'version': '11.0.1.0.1',
    'summary': 'Theme for Las Rías website',
    'description': '',
    'category': 'Theme',
    'author': 'Comunitea',
    'website': 'http://www.comunitea.com',
    'license': 'AGPL-3',
    'contributors': [
        'Vicente Ángel Gutiérrez <vicente@comunitea.com>',
        'Rubén Seijas <ruben@comunitea.com>',
    ],
    'depends': [
        # Custom
        'breadcrumbs_base',
        'ecommerce_base',
        'website_base_rias',
        # OCA
        'website',
        'website_sale',
        'website_slides',
        'website_form',
        'website_sale_hide_empty_category'
    ],
    'data': [
        'data/menu_data.xml',
        'data/page_data.xml',
        'data/slides_data.xml',
        'data/post_data.xml',
        'data/category_data.xml',
        'templates/snippets.xml',
        'templates/head.xml',
        'templates/header.xml',
        'templates/footer.xml',
        'templates/page_home.xml',
        'templates/page_our_shops.xml',
        'templates/page_catalogues.xml',
        'templates/page_about_us.xml',
        'templates/catalogue.xml',
        'templates/blog_post.xml',
        'templates/forms.xml',
        'templates/page_pricelist.xml',
        'views/category.xml',
        'templates/shop.xml'
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
