# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Pricelist Custom',
    'summary': 'Cutomizations over pricelist',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'product',
        'sale',
    ],
    'data': [
        'views/product_pricelist_view.xml',
    ],
}