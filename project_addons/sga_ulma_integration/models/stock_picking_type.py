# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _

class StockPickingTypeSGA(models.Model):

    _inherit = "stock.picking.type"

    ulma_integrated = fields.Boolean('Integrado con Ulma',
                                    help="If checked, odoo export this pick type to Adaia")
    ulma_type = fields.Selection([('SUBPAL', 'Palets'), ('SUBUNI', 'Cajas')], 'Typo de almacén')

    def get_sga_integrated(self):
        return self.ulma_integrated or super().get_sga_integrated()

