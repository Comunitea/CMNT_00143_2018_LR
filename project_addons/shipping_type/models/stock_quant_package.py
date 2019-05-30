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

    def get_picking_id(self):

        picks = self.mapped('move_line_ids').mapped('picking_id')
        return picks or False

    @api.multi
    def write(self, vals):
        child_vals = self.get_child_vals(vals)
        if child_vals:
            ctx = self._context.copy()
            ctx.update(write_from_package=True)
            # si está en un albarán no se puede modificar a noser que sea el propio albaran
            if self.filtered(lambda x: x.get_picking_id()) and not self._context.get('write_from_pick', False):
                raise ValidationError('Hay paquetes en un albarán. Debes cambiar los datos de envío en el albaran')
            self.mapped('move_line_ids').mapped('move_id').with_context(ctx).write(child_vals)
        super().write(vals)

