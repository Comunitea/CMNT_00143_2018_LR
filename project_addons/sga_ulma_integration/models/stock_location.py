# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
import datetime, time
from odoo.exceptions import UserError

class StockLocation(models.Model):

    _inherit = "stock.location"

    ulma_type = fields.Selection(related='picking_type_id.ulma_type')