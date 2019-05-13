# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'ADR Product',
    'summary': 'ADR product reports',
    'version': '11.0.1.0.0',
    'category': 'custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'sale',
        'stock',  # Mete el campo de productos alternativos
        'stock_batch_picking_lr'
    ],
    'data': [
        'views/product.xml',
        'views/sale_order.xml',
        'security/ir.model.access.csv',
        'report/report_delivery_batch_adr_views.xml',
        'data/adr_code.xml',
        'views/stock_delivery_batch_views.xml'
    ],
}