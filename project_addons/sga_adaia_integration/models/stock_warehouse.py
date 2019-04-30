# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _

class StockWarehouseSGA(models.Model):

    _inherit = "stock.warehouse"
    sga_integrated = fields.Boolean('Integrado con Adaia',
                                    help="If checked, odoo export this pick type to Adaia")