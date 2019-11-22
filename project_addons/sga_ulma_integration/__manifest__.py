# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'ULMA integration for Odoo',
    'summary': 'Stock picking integration Odoo-ULMA',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock',
        'stock_move_selection_wzd',
        'ftp_folder_sync'
    ],
    'data': ['views/res_config_views.xml',
        'data/sga_data.xml',
        'views/stock_picking_views.xml',
        'views/ulma_processed_mmmout.xml',
        'views/ulma_processed_mmminp.xml',
        'views/ulma_processed_containers.xml',
        'security/ir.model.access.csv',
        'views/stock_location_views.xml'
    ]
}