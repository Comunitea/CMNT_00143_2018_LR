# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Partner Reservation Days Custom',
    'summary': 'Partner reservation days',
    'version': '11.0.1.0.0',
    'category': 'stock',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'sale_stock',
        'procurement_jit',
        'web_tree_dynamic_colored_field_custom'
    ],
    'data': [
        'views/res_partner.xml',
        'views/stock_move.xml',
        'views/sale_order.xml',
    ],
}
