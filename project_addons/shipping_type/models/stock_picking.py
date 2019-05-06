# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = "stock.picking"

    shipping_type = fields.Selection(
        [('pasaran', 'Pasarán'),
         ('agency', 'Agencia'),
         ('route', 'Ruta')],
        string='Tipo de envío',
        help="Tipo de envío seleccionado."
    )


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    shipping_type = fields.Selection(
        [('pasaran', 'Pasarán'),
         ('agency', 'Agencia'),
         ('route', 'Ruta')],
        string='Tipo de envío',
        help="Tipo de envío seleccionado.",
        )

class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_new_picking_domain(self):
        domain = super()._get_new_picking_domain()
        if self.move_line_ids and self.move_line_ids[0].shipping_type:
            domain += [('shipping_type', '=', self.move_line_ids[0].shipping_type)]
        return domain