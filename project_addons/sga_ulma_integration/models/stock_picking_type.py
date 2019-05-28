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

    def get_ulma_vals(self, type=''):

        if self.group_code=='picking':
            mmmCMDREF = 'SAL'

        if self.group_code=='location':
            mmmCMDREF = 'ENT'

        vals = {'mmmdisref': self.ulma_type,
                'mmmsesid': 1 if self.ulma_type == 'SUBUNI' else 2,
                'mmmcod': 1,
                'mmmcmdref': mmmCMDREF,
                'mmmartean': 'ean13',
                'mmmges': 'ULMA',
                'mmmres': 'FINPED'}

        if type =="sale":
            vals.update({
                'mmmres': 'FIN',
            })

        if type == "move":
            vals.update({
                'mmmartapi': 0,
                'mmmres':'',
                'mmmminudsdis': 1})

        if type == "hueco":
            vals.update({
                'mmmres': '',
                'mmmubidesref': '01P010011',
                'mmmartean': '',
                'mmmmonlot': 1,
                'mmmrecref': 0,
                'mmmartapi': 0,
                'mmmcod': ''
            })

        if type == "caja":
            vals.update({
                'mmmres': 'FIN',
                'mmmubidesref': '01P010011',
                'mmmartean': '',
                'mmmmonlot': '',
                'mmmrecref': 0,
                'mmmartapi': 0,
                'mmmcod': ''

            })
        return vals