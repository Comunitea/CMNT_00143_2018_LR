# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class ProductProduct(models.Model):

    _inherit = 'product.product'

    abc_classification = fields.Selection([
            ('A', 'A'),
            ('A1', 'A1'),
            ('A2', 'A2'),
            ('B', 'B'),
            ('B1', 'B1'),
            ('C', 'C'),
            ('C1', 'C1'),
            ('C2', 'C2'),
        ], 'ABC Classification')


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    abc_classification = fields.Selection([
            ('A', 'A'),
            ('A1', 'A1'),
            ('A2', 'A2'),
            ('B', 'B'),
            ('B1', 'B1'),
            ('C', 'C'),
            ('C1', 'C1'),
            ('C2', 'C2'),
        ], 'ABC Classification',
        related='product_variant_ids.abc_classification', store=True)