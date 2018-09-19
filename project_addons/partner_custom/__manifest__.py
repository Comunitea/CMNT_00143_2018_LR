# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Custom Partner',
    'summary': 'Add custom partner para las rias',
    'version': '11.0.1.0.0',
    'category': 'Partner',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base','account','sale', 'contract'

    ],
    'data': [
        'data/analytic_tag.xml',
        'views/res_partner.xml',
        'views/config_file.xml',
        'views/sale_view.xml',
    ],
}
