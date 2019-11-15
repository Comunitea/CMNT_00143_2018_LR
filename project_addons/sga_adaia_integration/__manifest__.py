# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'ADAIA integration for Odoo',
    'summary': 'Stock picking integration Odoo-ADAIA',
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
        'stock_move_selection_wzd',
        'ftp_folder_sync'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking.xml',
        'views/stock_warehouse.xml',
        'views/sga_file.xml',
        'views/sga_error.xml',
        'views/res_partner.xml',
        'views/product_product.xml',
        'views/product_template.xml',
        'wizard/check_adaia_stock.xml',
        'wizard/stock_picking_adaia_confirm.xml',
        'data/sga_data.xml'
    ]
}