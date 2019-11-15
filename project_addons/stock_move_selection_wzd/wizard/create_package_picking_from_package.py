# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

class CreatePackagePickFromPackageWzd(models.TransientModel):
    _name = 'packaging.pick.from.package.wzd'

    package_id = fields.Many2one('stock.quant.package', 'Paquete que moveremos')
    batch_picking_id = fields.Many2one('stock.batch.picking', 'Albarán de cliente asociado')


    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)
        package_id = self._context.get('active_id', False)
        if package_id:
            move_lines = self.env['stock.move.line'].search([('result_package_id', '=', package_id)])
            move_ids = move_lines.mapped('move_id')
            batch_picking_id = move_ids.mapped('batch_picking_id')
            if not batch_picking_id:
                batch_picking_id = move_ids.mapped('draft_batch_picking_id')
            if not batch_picking_id:
                return defaults
            if len(batch_picking_id)!= 1:
                raise ValidationError (_('El paquete esta en varios albaranes'))

            defaults.update({'package_id': package_id, 'batch_picking_id': batch_picking_id.id})
        return defaults

    @api.multi
    def create_pick(self):
        package = self.package_id
        batch_picking_id = self.batch_picking_id
        new_batch = package.picking_pack_lines(batch_picking_id)
        action = new_batch.get_formview_action()
        return action
