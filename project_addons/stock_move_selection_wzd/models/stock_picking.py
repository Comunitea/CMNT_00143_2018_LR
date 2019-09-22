# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


from .stock_picking_type import PICKING_TYPE_GROUP
from .stock_picking_type import SGA_STATES

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sga_integrated = fields.Boolean('Sga', help='Marcar si tiene un tipo de integración con el sga')
    sga_state = fields.Selection(SGA_STATES, default='no_integrated', string="SGA Estado", copy=False)
    #state = fields.Selection(selection_add=[('packaging', 'Empaquetado')])

    def create_second_pick(self, second_moves=[]):
        """ Copy of create backorder
        """
        second_pick = self.env['stock.picking']
        if second_moves:
            second_pick = self.copy({
                    'name': '/',
                    'move_lines': [],
                    'move_line_ids': [],
                    'second_id': self.id
                })
            self.message_post(
                _('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                    second_pick.id, second_pick.name))
            second_moves.write({'picking_id': second_pick.id})
            second_moves.mapped('move_line_ids').write({'picking_id': second_pick.id})
            second_pick.action_assign()
        return second_pick

    @api.model
    def create(self, vals):

        if len(vals) == 1 and vals.get('name', False):
            domain = [('name', '=', vals.get('name', False))]
            picking_type_id = self.env['stock.picking.type'].search(domain)
            if not picking_type_id:
                raise ValidationError (_("Not pick for '%s'") % vals.get('name', False))
            if len(picking_type_id)>1:
                raise ValidationError (_("More than 1 pick for '%s'") % vals.get('name', False))
            vals.update(picking_type_id=picking_type_id.id,
                        sga_integrated=picking_type_id.get_sga_integrated(),
                        sga_state = 'no_send' if picking_type_id.get_sga_integrated() else 'no_integrated',
                        location_id=picking_type_id.default_location_src_id.id,
                        location_dest_id=picking_type_id.default_location_dest_id.id)
            vals.pop('name')
        return super().create(vals)

    def get_new_vals(self):
        vals = {'shipping_type': self.shipping_type,
                'delivery_route_path_id': self.delivery_route_path_id.id,
                'urgent': self.urgent,
                'carrier_id': self.carrier_id.id
                }
        return vals

    def action_send_to_sga(self):
        return self.send_to_sga()

    @api.multi
    def send_to_sga(self):
        ##PARA HEREDAR EN ULMA Y ADAIA
        return True


