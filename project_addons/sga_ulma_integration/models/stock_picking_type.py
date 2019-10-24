# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError, ValidationError

class StockPickingTypeSGA(models.Model):

    _inherit = "stock.picking.type"

    ulma_type = fields.Selection([('SUBPAL', 'Palets'), ('SUBUNI', 'Cajas')], 'Typo de almacén')

    def get_sga_integrated(self):
        return self.sga_integrated or super().get_sga_integrated()

    def get_ulma_vals(self, type='', partner_id=None, picking_id=None):

        if self.group_code == 'picking':
            mmmCMDREF = 'SAL'
        elif self.group_code == 'location':
            mmmCMDREF = 'ENT'
        else:
            raise ValidationError ('Tipo no permitido')

        vals = {'mmmdisref': self.ulma_type,
                'mmmsesid': 1 if self.ulma_type == 'SUBUNI' else 2,
                'mmmcmdref': mmmCMDREF,
                'mmmartean': 'ean13',
                'mmmges': 'ULMA',
                'mmmres': 'FINPED'}

        if type =="sale":
            vals.update({
                'mmmres': 'FIN',
                'mmmentdes': '{} ({})'.format(partner_id.name, picking_id.name),
                'mmmentdir1': '{} {}'.format(partner_id.street, partner_id.street2 if partner_id.street2 else ''),
                'mmmentdir2': partner_id.city,
                'mmmentdir3': partner_id.state_id.name if partner_id.state_id else partner_id.city,
                'mmmentdir4': partner_id.zip,
                'mmmacccolcod': picking_id.id
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
            })

        if type == "caja":
            vals.update({
                'mmmres': 'FIN',
                'mmmubidesref': '01P010011',
                'mmmartean': '',
                'mmmmonlot': '',
                'mmmrecref': 0,
                'mmmartapi': 0
            })
        return vals