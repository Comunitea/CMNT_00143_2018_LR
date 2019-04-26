# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Campaign',
    'summary': 'Adds the campaign model',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'account',
        'sale',
        'purchase'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/campaign.xml',
        'views/sale_order_view.xml',
        'views/purchase_view.xml',
    ],
}
