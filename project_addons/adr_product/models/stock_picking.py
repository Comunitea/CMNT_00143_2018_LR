# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    _order = "name, id, sequence"

    @api.multi
    def _get_adr_picking_value(self):
        for pick in self:
            pick.adr = any(x.product_id.product_tmpl_id.adr_idnumonu for x in pick.move_lines)

    adr = fields.Boolean('Adr', compute="_get_adr_picking_value", readonly=1)
    adr_packing_list = fields.Many2one('adr.packing.list', 'Adr packing list')
    #Revisar por qué no va
    sequence = fields.Integer(string="Sequence", default=10)

class StockBatchPicking(models.Model):
    _inherit = "stock.batch.picking"

    @api.multi
    def _get_adr_picking_value(self):
        for pick in self:
            pick.adr = any(x.product_id.product_tmpl_id.adr_idnumonu for x in pick.move_lines)

    adr = fields.Boolean('Adr', compute="_get_adr_picking_value", readonly=1)
    adr_packing_list = fields.Many2one('adr.packing.list', 'Adr packing list')


