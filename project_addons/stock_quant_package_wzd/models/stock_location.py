# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo import exceptions

class StockLocation(models.Model):
    _inherit = 'stock.location'

    preparation_location = fields.Boolean('Ubiación de preparación', default=False)
