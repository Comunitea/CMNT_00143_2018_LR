# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Stock Quant Package Selection Wzd',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'stock_move_selection_wzd',
    ],
    'data': [
        'views/stock_quant_package.xml',
        'views/stock_location.xml',
        'views/stock_delivery_batch.xml',
        'views/stock_picking_type.xml',
        'views/menus_stock_quant_package.xml',
    ],
    'installable': True,
}


