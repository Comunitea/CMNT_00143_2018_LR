# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account invoice upload sqlserver',
    'version': '11.0.1.0.0',
    'summary': 'Upload invoice pdf to sql server',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'account_payment_order',
        'queue_job'
    ],
    'external_dependencies': {
        'python': [
            'pyodbc',
        ],
    },
    'data': [
        'data/parameters.xml',
        'views/sqlserver_config.xml',
        'views/account_journal.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
