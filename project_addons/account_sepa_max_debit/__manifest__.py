# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Maximum Debit Amount ',
    'summary': 'Limit the maximun amount by debit order',
    'version': '11.0.1.0.0',
    'category': 'Payment',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'account_payment_order',
        'account_banking_sepa_direct_debit'

    ],
    'data': [
        'views/res_partner.xml',
        'views/mandate.xml',
        'views/account_payment_order_view.xml',
    ],
}
