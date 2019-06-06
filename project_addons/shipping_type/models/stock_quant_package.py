# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from .res_partner import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

class StockQuantPackage(models.Model):
    _inherit = ['stock.quant.package', 'info.route.mixin']
    _name = 'stock.quant.package'

    @api.multi
    def _count_move_line_ids(self):
        for pack in self:
            pack.count_move_line = len(pack.move_line_ids)

    dest_partner_id = fields.Many2one("res.partner")
    partner_shipping_type = fields.Char('')#Selection(related="dest_partner_id.shipping_type")
    count_move_line = fields.Integer(compute=_count_move_line_ids)
    picking_id = fields.Many2one('stock.picking')
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    campaign_id = fields.Many2one('campaign', 'Campaign')


    def propagate_route_vals(self, vals):
        ctx = self._context.copy()
        ctx.update(write_from_picking=True)
        move_vals= {}
        if 'picking_id' in vals:
            picking_id = vals['picking_id']
            move_vals.update({'picking_id': vals['picking_id']})
            pick = self.env['stock.picking'].browse(picking_id)
            if pick:
                child_vals = pick.get_child_vals(vals)
                if child_vals:
                    move_vals.update(child_vals)

            ctx = self._context.copy()
            ctx.update(write_from_package=True, write_from_picking=True)
            self.mapped('move_line_ids').mapped('move_id').with_context(ctx).write(move_vals)
        else:
            child_vals = self.get_child_vals(vals)
            if child_vals:
                if self.mapped('picking_id') and not self._context.get('write_from_pick', False):
                    raise ValidationError ('No puedes cambiar estos valores en el paquete si ya está en un albarán')
                ctx = self._context.copy()
                ctx.update(write_from_package=True)
                move_vals.update(child_vals)
                self.mapped('move_line_ids').mapped('move_id').with_context(ctx).write(move_vals)

    @api.multi
    def write(self, vals):
        if self._context.get('no_propagate_route_vals', True):
            self.propagate_route_vals(vals)

        super().write(vals)
        if 'move_line_ids' in vals:
            for pack in self:
                picking_id = pack.move_line_ids.mapped('picking_id')
                pack.picking_id = picking_id and picking_id[0]





