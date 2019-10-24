# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Shipping Type',
    'summary': 'Add functions to select default shipping types for partners',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'sale_stock',
        'stock_picking_group',
        'stock_batch_picking',
        'campaign'

    ],
    'data': [
        'views/res_partner_view.xml',
        'views/sale_order.xml',
        'views/stock_quant_package.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
        'views/stock_batch_picking.xml',
        #'views/delivery_route_path.xml'
    ],
}