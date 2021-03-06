# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time
from odoo.exceptions import UserError
from odoo.addons.stock_move_selection_wzd.models.stock_picking_type import SGA_STATES


class StockPicking(models.Model):

    _inherit = "stock.picking"

    ulma_error = fields.Text(default="", string="Error msg in case the Ulma integration failed")
    sga_integrated = fields.Boolean(related='picking_type_id.sga_integrated')
    sga_integration_type = fields.Selection(related="picking_type_id.sga_integration_type")

    @api.multi
    def get_picks_ulma_pending(self):
        sm = self.env['stock.move']
        sm_domain = [('picking_type_id.sga_integration_type', '=', 'sga_ulma'), ('sga_state', '=', 'pending'), ('state', 'not in', ('done', 'cancel'))]
        ids = sm.search(sm_domain).mapped('picking_id')
        return ids

    def get_vals_picking_to_ulma(self, batch, ulma_move='', date_expected=''):
        partner_id = self.partner_id
        vals = batch.picking_type_id.get_ulma_vals('sale', partner_id, self)
        
        if self.shipping_type == 'route':
            shipping_type_letter = 'N'
            shipping_type_full = 'RUTA'
        elif self.shipping_type == 'pasaran':
            shipping_type_letter = 'P'
            shipping_type_full = 'PASARAN'
        else:
            shipping_type_letter = 'H'
            shipping_type_full = 'AGENCIA'

        update_vals = {
            'mmmexpordref': '{}{}'.format(shipping_type_letter, self.name.zfill(8)),
            'mmmsesid': 1 if batch.picking_type_id.ulma_type == 'SUBUNI' else 2,
            'momcre': "{}".format(datetime.datetime.now()),
            'mmmterref': partner_id.ref or None,
            'mmmbatch': batch.name[-9:],
            'mmmacccolcod': self.id,
            'mmmmomexp': "{}".format(datetime.datetime.now()),
            'mmmurgnte': 'S' if batch.shipping_type == 'urgent' else 'N',
            'mmmtraref': '{}-{}'.format(self.delivery_route_path_id.name if self.delivery_route_path_id.name else 'Sin ruta', shipping_type_full)
        }

        vals.update(update_vals)
        return vals

    def force_button_validate(self):
        self.sga_state = 'done'
        return self.button_validate()  