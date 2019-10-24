# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Inter Company Module for Purchase to Sale Order',
    'summary': 'Intercompany PO/SO rules',
    'version': '11.0.1.0.0',
    'category': 'Purchase Management',
    'website': 'http://www.github.com/OCA/multi-company',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'stock_dropshipping',
        'purchase_sale_inter_company'
    ],
    'data': [
    'views/stock_picking.xml'
    ],
}
