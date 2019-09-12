# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from .stock_picking_type import SGA_STATES

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    sga_integrated = fields.Boolean('Sga', help='Marcar si tiene un tipo de integración con el sga')
    sga_state = fields.Selection(SGA_STATES, default='NI', string="SGA Estado")

    @api.multi
    def write(self, vals):
        return super().write(vals)
