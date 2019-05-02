# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _

class StockPickingTypeSGA(models.Model):

    _inherit = "stock.picking.type"

    sga_integrated = fields.Boolean('Integrado con Adaia',
                                    help="If checked, odoo export this pick type to Adaia")
    sgavar_file_id = fields.Many2one('sgavar.file', 'SGA Type')

class StockPickingSGAType(models.Model):

    _name = "stock.picking.sgatype"
    _rec_name = "code"

    code = fields.Char("Tipo de venta (SGA)", size=30, default="CORDER")
    description = fields.Char("Descripcion (SGA)", size=100)