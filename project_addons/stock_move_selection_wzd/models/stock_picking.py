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
    sga_state = fields.Selection(SGA_STATES, default='NI', string="SGA Estado")
    state = fields.Selection(selection_add=[('packaging', 'Empaquetado')])


    @api.depends('move_type', 'move_lines.state', 'move_lines.picking_id', 'move_line_ids.result_package_id')
    @api.one
    def _compute_state(self):

        super()._compute_state()
        for pick in self.filtered (lambda x: x.picking_type_id.group_code == 'outgoing' and x.state == 'assigned'):
            if pick.move_line_ids.filtered(lambda x: x.result_package_id == False):
                pick.state = 'packaging'


    @api.multi
    def action_done(self):
        ctx = self._context.copy()
        ctx.update(write_from_picking=True)
        for pick in self:
            if pick.state == 'packaging':
                raise ValidationError ('No puedes validar el albarán {} porque está en empaquetado'.format(pick.name))
        return super(StockPicking, self.with_context(ctx)).action_done()

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
                        sga_state = 'NE' if picking_type_id.get_sga_integrated() else 'NI',
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


