# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Move APK',
    'summary': 'Add functions for stock move apk',
    'version': '11.0.1.0.0',
    'category': 'warehouse',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock',
        'sale',
        'shipping_type'
    ],
    'data': [
        'views/move_apk_views.xml',
        'security/ir.model.access.csv'
    ]
}