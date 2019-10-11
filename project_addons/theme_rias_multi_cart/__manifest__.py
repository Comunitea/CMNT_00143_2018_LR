# -*- coding: utf-8 -*-
# © 2019 Comunitea - 
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Theme Rías Multi Cart',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'theme_rias',
        #'sale_variant_configurator', Se comenta par apoder desinstalar este
        # módulo
        'campaign',
    ],
    'data': [
        'data/page_data.xml',
        'data/menu_data.xml',
        'templates/head.xml',
        'templates/shop.xml',
        'templates/portal.xml',
        'templates/header.xml',
        ],
    'images': [
        '/static/description/icon.png',
    ],
    'installable': True,
}