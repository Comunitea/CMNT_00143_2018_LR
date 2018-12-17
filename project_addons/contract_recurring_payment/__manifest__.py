# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'contract recurring payment',
    'version': '11.0.1.0.0',
    'summary': 'Create recurring payment orders from contracts',
    'category': 'Account',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'contract',
        'account_banking_mandate'
    ],
    'data': [
        'views/account_analytic_contract.xml',
        'views/account_analytic_account.xml',
        'views/account_voucher_contract.xml',
        'data/payment_cron.xml'
    ],
}
