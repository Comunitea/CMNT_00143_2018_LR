# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Stock Move Selection Wzd',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'sale_stock',
        'stock_picking_imp',
        'stock_picking_group',
        'shipping_type'

    ],
    'data': [
        'views/stock_move.xml',
        'views/picking_type.xml',
        'views/stock_picking.xml',
        'views/stock_quant_package.xml',
        'wizard/batch_picking_wzd_view.xml',
        'wizard/move_change_quant_wzd.xml',

    ],
    'installable': True,
}
