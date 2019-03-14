# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api, fields


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    aeoc_id = fields.Many2one('aeoc.classification', 'AEOC Classification')