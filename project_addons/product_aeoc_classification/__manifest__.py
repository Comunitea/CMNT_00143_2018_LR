# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Product AEOC Classification',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'product',
        'sale' 
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/aeoc_classification_view.xml',
        'views/product_template_view.xml'
    ],
    'installable': True,
}
