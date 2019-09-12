# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = "product.template"

    adr_idnumonu = fields.Many2one('product.adr.code', string='ADR Code')
    adr_weight_x_kgrs_11363 = fields.Float(compute="_weight_calculator")
    adr_weight_x_kgrs_11364 = fields.Float(compute="_weight_calculator")

    adr_denomtecnica = fields.Char('Denominación técnica')
    adr_peligroma = fields.Boolean('Artículo peligroso')
    adr_exe22315 = fields.Boolean ('Sujeto a la exención 22315')
    adr_bultodesc = fields.Char("Descripción del bulto")

    @api.multi
    @api.depends('adr_idnumonu.multiplier', 'weight', 'adr_idnumonu.adr_category_id')
    def _weight_calculator(self):

        for product in self:
            if product.adr_idnumonu.multiplier and product.adr_idnumonu.multiplier is not 0:
                product.adr_weight_x_kgrs_11363 = product.weight*product.adr_idnumonu.multiplier
                product.adr_weight_x_kgrs_11364 = product.weight*product.adr_idnumonu.adr_category_id.x_kgrs_11364
            else:
                product.adr_weight_x_kgrs_11363 = product.weight*product.adr_idnumonu.adr_category_id.x_kgrs_11363
                product.adr_weight_x_kgrs_11364 = product.weight*product.adr_idnumonu.adr_category_id.x_kgrs_11364



