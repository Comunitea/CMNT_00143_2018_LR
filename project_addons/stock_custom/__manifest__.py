# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Stock Custom',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'product',
        'stock',
        'stock_picking_report_valued',
        'stock_batch_picking',
        'stock_picking_group',
        'chained_discount'
    ],
    'data': [
        'data/cron.xml',
        'data/product.xml',
        'views/product_view.xml',
        'views/stock_rotation_history_view.xml',
        'views/stock_warehouse_view.xml',
        'views/report_batch_picking.xml',
        'views/res_company.xml',
        'views/sale.xml',
        'views/res_config_settings.xml',
        'views/account_invoice.xml',
        'wizard/sale_invoice_on_date.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
