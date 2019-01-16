# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Import out invoices',
    'version': '11.0.1.0.0',
    'author': 'Comunitea',
    'website': 'www.comunitea.com',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'account_invoice_custom'
    ],
    'data': [
        'wizard/account_import_invoice.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
