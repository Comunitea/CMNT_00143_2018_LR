# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Delivery Batch',
    'version': '1.0',
    'category': 'Custom',
    'description': "Module to manage delivery batches",
    'depends': ['stock', 'adr_product', 'delivery'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_delivery_batch_views.xml',
        'views/delivery_carrier_views.xml',
        'report/report_delivery_batch_custom_views.xml',
        'wizard/stock_picking_to_delivery_views.xml',
        'data/stock_delivery_batch_data.xml'
    ],
    'demo': [

    ],
    'installable': True,
}
