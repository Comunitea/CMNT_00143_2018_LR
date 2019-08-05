# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Stock Custom',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'product',
        'stock'
    ],
    'data': [
        'data/cron.xml',
        'views/product_view.xml',
        'views/sale.xml',
        'views/stock_rotation_history_view.xml',
        'wizard/sale_invoice_on_date.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
