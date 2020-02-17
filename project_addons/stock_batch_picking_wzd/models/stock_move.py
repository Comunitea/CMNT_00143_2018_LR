# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class StockMove(models.Model):

    _inherit = "stock.move"


    @api.multi
    def add_moves_to_expedition(self):
        moves_in_self = self.filtered(lambda x: x.to_batch != False)
        batch_picking_id = moves_in_self[0].to_batch
        if not batch_picking_id:
            return
        picks_in_self = self.mapped('picking_id')
        moves_not_in_self = picks_in_self - moves_in_self
        new_picks = picks_in_self.split_if_moves(batch_picking_id, moves_not_in_self)
        picks_in_self.write({'batch_picking_id': batch_picking_id})

    def _get_new_picking_domain(self):
        domain = super()._get_new_picking_domain()
        return domain
