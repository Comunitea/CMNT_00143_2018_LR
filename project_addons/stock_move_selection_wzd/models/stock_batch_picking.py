# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from odoo.exceptions import ValidationError

class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    @api.multi
    def _get_effective_move_lines(self):
        for batch_picking_id in self:
            if batch_picking_id.picking_type_id.sga_integrated:
                batch_picking_id.effective_move_lines = batch_picking_id.move_lines.filtered(
                    lambda x: x.sga_state not in ('PE', 'SR', 'SC') and x.reserved_availability > 0)
            else:
                batch_picking_id.effective_move_lines = batch_picking_id.move_lines.filtered(
                    lambda x: x.reserved_availability > 0)

    batch_delivery_id = fields.Many2one('stock.batch.delivery', string="Delivery batch")
    picking_type_id = fields.Many2one(string='Picking type', comodel_name='stock.picking.type', required=True, readonly=True, states={'draft': [('readonly', False)]},)
    effective_move_lines = fields.One2many('stock.move', string='Movimientos', compute=_get_effective_move_lines)


    @api.onchange('picking_ids')
    def onchange_picking_ids(self):
        for batch in self:
            if all(pick.picking_type_id == batch.picking_type_id for pick in batch.picking_ids):
                continue
            raise ValidationError ("Todos los albaranes deben de ser del mismo tipo ({})".format(batch.picking_type_id.name))

    @api.multi
    def write(self, vals):
        return super().write(vals)

    @api.multi
    def action_see_packages(self):
        self.ensure_one()
        action = self.env.ref('stock.action_package_view').read()[0]
        packages = self.move_line_ids.mapped('result_package_id')
        action['domain'] = [('id', 'in', packages.ids)]
        return action



    @api.multi
    def batch_printing(self):
        pickings = self.mapped('picking_ids')
        if not pickings:
            raise ValidationError(_('Nothing to print.'))
        else:
            active_ids = []
            for batch in self:
                active_ids.append(batch.id)
            return self.env.ref('stock_move_selection_wzd.delivery_batch_report').with_context(active_ids=active_ids, active_model='stock.batch.picking', pickings=pickings).report_action([])