# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Direct invoices',
    'summary': 'Importa facturas de directo, crea una factura al socio con % de colaboración. Y factura de proveedor al proveedor',
    'version': '11.0.1.0.0',
    'category': 'Account',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'account_invoice',

    ],
    'data': [
        'views/account.xml'
    ],
}
