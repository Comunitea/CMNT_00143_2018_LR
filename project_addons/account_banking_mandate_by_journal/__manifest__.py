# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account banking mandate by journal',
    'version': '11.0.1.0.0',
    'summary': 'Allows to specify a journal for each mandate',
    'category': 'Account',
    'author': 'comunitea',
    'website': 'www.comunitea.com',
    'license': 'AGPL-3',
    'depends': [
        'account_banking_mandate',
        'account_shipping_address'
    ],
    'data': [
        'views/account_banking_mandate.xml'
    ],
    'installable': True,
}
