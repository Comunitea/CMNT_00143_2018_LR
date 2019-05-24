# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


PICKING_TYPE_GROUP = [('incoming', 'Incoming'),
                      ('outgoing', 'Outgoing'),
                      ('picking', 'Picking'),
                      ('internal', 'Internal'),
                      ('location','Location'),
                      ('reposition','Reposition'),
                      ('other','Other')]


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    group_code = fields.Selection(PICKING_TYPE_GROUP, string="Code group")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

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
                        location_id=picking_type_id.default_location_src_id.id,
                        location_dest_id=picking_type_id.default_location_dest_id.id)
            vals.pop('name')
        return super().create(vals)
