# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from odoo.exceptions import UserError

from pprint import pprint

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):

        res = super()._get_new_picking_values()
        res['batch_picking_id'] = self._context.get('batch_picking_id', False)
        res['origin'] = self.origin
        return res