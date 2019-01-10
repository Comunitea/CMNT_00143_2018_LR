# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Virtual Fair',
    'summary': 'Adds the virtual fair model and an importer',
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
        'partner_custom',
        'base_multi_image',
        'invoice_early_payment_discount'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/parameter.xml',
        'data/product_data.xml',
        'views/account_invoice_history.xml',
        'views/virtual_fair.xml',
        'views/importation_log.xml',
        'views/res_company.xml',
        'views/account_invoice.xml',
        'wizard/virtual_fair_import_wzd.xml',
        'wizard/invoice_supplier_import_wzd.xml',
        'wizard/direct_invoice_wzd.xml',
        'wizard/duplicate_invoice_manual_check.xml',
        'wizard/account_invoice_refund_wizard.xml'
    ],
}
