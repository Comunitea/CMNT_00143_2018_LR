# -*- coding: utf-8 -*-
# © 2019 Comunitea - 
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Theme Rías Menu',
    'version': '11.0.1.0.1',
    'summary': 'Add an Snippet Content Menu by customizable view',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        # Custom
        'theme_rias',
        # Odoo
        'website',
    ],
    'data': [
        # 'data/menu_data.xml',
        'views/website_menu_view.xml',
        'templates/snippets.xml',
        'templates/header.xml',
        'templates/head.xml'
        ],
    'images': [
        '/static/description/icon.png',
    ],
    'installable': True,
}
