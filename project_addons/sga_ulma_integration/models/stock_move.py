# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time
from odoo.exceptions import UserError

class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    def get_move_line_ulma_vals(self, cont=0, sale_id=False):

        sale_id = sale_id or self.move_id.sale_id
        if sale_id.shipping_type == 'pasaran':
            cte1 = 'P'
        elif sale_id.shipping_type == 'urgent':
            cte1 = 'H'
        else:
            cte1 = 'N'
        vals = self.move_id.picking_type_id.get_ulma_vals('move')

        update_vals = {
            'mmmartdes':  self.product_id.display_name[:40],
            'mmmartref': self.product_id.default_code,
            'mmmcanuni': self.product_uom_qty,
            'mmmexpordref': '{}{}'.format(cte1, sale_id.name)[9:], ##pick.name
            'mmmsecada': self.id,
            'momcre': datetime.datetime.now(),
            'mmmacccod': cont,
            'mmmbatch': self.draft_batch_picking_id.name[-9:],
            'mmmacccolcod': self.picking_id.id,
            'mmmmomexp': datetime.datetime.strptime(self.move_id.date_expected, '%Y-%m-%d %H:%M:%S'),
            'mmmfeccad': datetime.datetime.strptime(self.move_id.date_expected, '%Y-%m-%d %H:%M:%S'),
            }
        vals.update(update_vals)
        return vals

class StockMove(models.Model):

    _inherit = "stock.move"

    def get_new_vals(self):
        return super().get_new_vals()

