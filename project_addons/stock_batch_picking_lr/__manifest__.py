# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Batch Picking Custom for Las Rías',
    'summary': 'Customizations over the module Stock Batch Picking from OCA',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock',
        'shipping_type',
        'stock_batch_picking',
        'stock_manual_picking_creation'
    ],
    'data': [
        'views/delivery_carrier_views.xml',
        'views/res_partner_views.xml',
        'views/stock_batch_picking_views.xml',
        'report/report_delivery_batch_views.xml'
    ]
}