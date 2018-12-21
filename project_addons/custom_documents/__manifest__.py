# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Custom documents',
    'version': '11.0.1.0.0',
    'category': '',
    'author': 'Coumnitea',
    'license': 'AGPL-3',
    'license': '',
    'depends': [
        'account',
        'account_due_dates_str',
        'base_multi_image'
    ],
    'data': [
        'views/report_invoice.xml',
        'views/report_templates.xml',
        'views/account_invoice.xml'
    ],
    'installable': True,
}