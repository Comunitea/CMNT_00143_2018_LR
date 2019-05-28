# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time
from odoo.exceptions import UserError
from pprint import pprint





class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    ulma_integrated = fields.Boolean('Ulma integrated')

    def get_move_line_ulma_vals(self, cont=0, sale_id=False):
        sale_id = sale_id or self.move_id.sale_id
        if sale_id.shipping_type == 'pasaran':
            cte1 = 'P'
        else:
            if sale_id.urgent:
                cte1='S'
            else:
                cte1='N'
        vals = {
            'mmmacccolcod': sale_id.id,
            'mmmartdes':  self.product_id.display_name[:40],
            'mmmartref': self.product_id.default_code,
            'mmmcanuni': self.product_uom_qty,
            'mmmcmdref': "SAL",
            'mmmdisref': self.move_id.picking_type_id.ulma_type,
            'mmmexpordref': '{}{}'.format(cte1, sale_id.name)[9:], ##pick.name
            'mmmges': "ULMA",
            'mmmres': "",
            'mmmsecada': self.id,
            'mmmsesid': 2 if self.move_id.picking_type_id.ulma_type == 'SUBPAL' else 1,
            'momcre': datetime.datetime.strptime(self.move_id.date, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d'),
            'mmmartean': "ean13",
            'mmmterref': None,
            'mmmacccod': cont,
            'mmmbatch': self.picking_id.name, #pick.batch_picking_id.name,
            'mmmmomexp': datetime.datetime.strptime(self.move_id.date_expected, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d'),
            'mmmfeccad': datetime.datetime.strptime(self.move_id.date_expected, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d'),
            'mmmartapi': 0,
            'mmmminudsdis': 1}
        pprint(vals)
        return vals

    @api.onchange('sga_state')
    @api.multi
    def onchange_sga_state(self):
        if self._context('no_update_sga_state', False):
            return
        move_ids = self.mapped('move_id')
        for sm in move_ids:
            sm.sga_state = self.get_parent_state(sm.move_line_ids)

class StockMove(models.Model):

    _inherit = "stock.move"

    ulma_integrated = fields.Boolean('Ulma integrated')

    def get_new_vals(self):
        return super().get_new_vals()

    @api.onchange('sga_state')
    @api.multi
    def onchange_sga_state(self):
        if self._context('no_update_sga_state', False):
            return
        picking_ids = self.mapped('picking_id')
        for pick in picking_ids:
            pick.sga_state = self.get_parent_state(pick.move_ids)