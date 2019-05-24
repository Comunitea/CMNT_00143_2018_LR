# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'ULMA integration for Odoo',
    'summary': 'Stock picking integration Odoo-ULMA',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'stock',
        'shipping_type',
        'stock_batch_picking',
        'stock_batch_picking_lr'
    ],
    'data': [
        'views/stock_batch_picking_views.xml',
        'views/stock_picking_views.xml',
        'views/ulma_mmmout.xml',
        'views/ulma_mmminp.xml',
        'views/ulma_packinglist.xml',
        'views/stock_quant_package_views.xml',
        'views/res_config_views.xml',
        'security/ir.model.access.csv'
    ]
}