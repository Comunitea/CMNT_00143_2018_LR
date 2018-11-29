# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Payment Custom ',
    'summary': 'Customizations over payments',
    'version': '11.0.1.0.0',
    'category': 'Payment',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'account_banking_sepa_direct_debit'

    ],
    'data': [
        'wizard/account_paymnet_line_create_view.xml',
        'wizard/bank_payment_line_set_journal.xml',
        'views/account_payment_order.xml',
        'views/bank_payment_line.xml'
    ]
}
