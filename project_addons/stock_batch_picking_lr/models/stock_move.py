# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from odoo.exceptions import UserError

from pprint import pprint


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_domain_batch_picking(self):
        domain = [('picking_type_id', '=', self.picking_type_id.id),
                  ('shipping_type', '=', self.shipping_type),
                  ('delivery_route_path_id', '=', self.delivery_route_path_id and self.delivery_route_path_id.id or False),
                  ('urgent', '=', self.urgent),
                  ('carrier_id', '=', self.carrier_id and self.carrier_id.id or False),
                  ('state', 'in', ('draft', 'assigned'))]

        return domain

    def get_new_batch_vals(self):
        vals = {'picking_type_id': self.picking_type_id.id,
                'shipping_type': self.shipping_type,
                'delivery_route_path_id': self.delivery_route_path_id and self.delivery_route_path_id.id or False,
                'carrier_id':  self.carrier_id and self.carrier_id.id or False,
                'urgent': self.urgent}
        return vals

    @api.multi
    def pick_assign_batch_picking(self):
        batch = self.env['stock.batch.picking']
        for pick in self:
            domain = pick.get_domain_batch_picking()
            batch_id = batch.search(domain, limit=1)
            if batch_id:
                vals = {'batch_picking_id': batch_id.id}
            else:
                batch_id = batch.create(pick.get_new_batch_vals())
                vals = {'batch_picking_id': batch_id.id}

            pick.write(vals)
            pick.move_line_ids.mapped('result_package_id').write(vals)

    @api.multi
    def write(self, vals):

        super().write(vals)
        if 'batch_picking_id' in vals:
            val = {'batch_picking_id': vals['batch_picking_id']}
            self.mapped('move_line_ids').mapped('result_package_id').write(val)



class StockMove(models.Model):
    _inherit = 'stock.move'

    batch_picking_id = fields.Many2one(related = 'picking_id.batch_picking_id')

    def _get_new_picking_values(self):
        res = super()._get_new_picking_values()
        if self._context.get('batch_picking_id', False):
            res['batch_picking_id'] = self._context.get('batch_picking_id', False)
        res['origin'] = self.origin
        return res

    def move_assign_batch_picking(self):
        ## SOlo puedo meter en porte si tiene albarán y paquete
        to_assign = self.filtered(lambda x: x.picking_id and x.result_package_id)
        if to_assign:
            picks = to_assign.mapped('picking_id')
            picks.pick_assign_batch_picking()

    def move_desassign_batch_picking(self):
        ## SOlo puedo meter en porte si tiene albarán y paquete
        batch_ids = self.mapped('picking_id').mapped('batch_picking_id').filtered(lambda x:x.state != 'done')
        batch_ids.unlink()