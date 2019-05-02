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
        'stock_picking_group'

    ],
    'data': [
        #'views/product_view.xml',
        'views/stock_move.xml',
        #'wizard/stock_move_selection_wzd.xml',

    ],
    'installable': True,
}
