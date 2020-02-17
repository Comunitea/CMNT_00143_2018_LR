# -*- coding: utf-8 -*-

{
    'name': 'Las Rias Website Base',
    'version': '11.0.1.1.0',
    'summary': 'Las Rias website customization for backend and common parts',
    'description': '',
    'category': 'Website',
    'author': 'Comunitea',
    'website': 'http://www.comunitea.com',
    'license': 'AGPL-3',
    'contributors': [
        'Vicente Gutierrez <vicente@comunitea.com>',
        'Rubén Seijas <ruben@comunitea.com>',
    ],
    'depends': [
        'ecommerce_base',
        'website_blog_base',
        'breadcrumbs_base_tmp',
        'seo_base',
        'purchase',
    ],
    'data': [
        'data/website_data.xml',
        'data/page_data.xml',
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
