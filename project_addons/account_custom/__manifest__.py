# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Custom ',
    'summary': 'Customizations over Account Models',
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
        'account_due_list',
        'email_template_qweb',
        'account_netting',
        'account_payment_order',
        'l10n_es_account_banking_sepa_fsdd'
    ],
    'data': [
        'data/invoice_mailing_template.xml',
        'wizard/invoice_mailing_wzd_view.xml',
        'views/account_move_line.xml',
        'views/account_payment_mode.xml',
        'data/netting_template.xml',
        'data/ir_cron.xml'
    ]
}
