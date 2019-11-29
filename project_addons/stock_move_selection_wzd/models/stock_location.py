# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class StockLocation(models.Model):

    _inherit="stock.location"

    manual_pick = fields.Boolean('Picking manual', help="Si está marcado, las salidas de esta ubicación saldrán listadas en la orden de carga")
