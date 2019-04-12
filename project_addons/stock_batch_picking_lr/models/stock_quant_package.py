# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from pprint import pprint

class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    stock_batch_id = fields.Many2one('stock.batch.picking', 'Stock Batch')