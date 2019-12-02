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

        vals = {
                'mmmcmdref': mmmCMDREF,
                'mmmdisref': self.ulma_type or None,
                'mmmges': 'ULMA',
                'mmmres': 'FINPED',
                'mmmsesid': 1 if self.ulma_type == 'SUBUNI' else 2,
                'momcre': None,
                'mmmartean': 'ean13',
                'mmmbatch': None,
                'mmmmomexp': None,
                'mmmacccolcod': None,
                'mmmentdes': None,
                'mmmexpordref': None,
                'mmmterref': None,
                'mmmentdir1': None,
                'mmmentdir2': None,
                'mmmentdir3': None,
                'mmmentdir4': None,
                'mmmurgnte': None,
                'mmmtraref': None,
                'mmmartdes': None,
                'mmmartref': None,
                'mmmcanuni': None,
                'mmmsecada': None,
                'mmmacccod': None,
                'mmmfeccad': None,
                'mmmartapi': None,
                'mmmminudsdis': None,
                'mmmabclog': None,
                'mmmdim': None,
                'mmmcntdorref': None,
                'mmmcrirot': None,
                'mmmdorhue': None,
                'mmmlot': None,
                'mmmmonlot': None,
                'mmmrecref': None,
                'mmmubidesref': None,
                'mmmzondesref': None,
                'mmmobs': None
            }

        if type =="sale":
            vals.update({
                'mmmres': 'FIN',
                'mmmentdes': '{} ({})'.format(partner_id.name, picking_id.name),
                'mmmentdir1': '{} {}'.format(partner_id.street, partner_id.street2 if partner_id.street2 else None),
                'mmmentdir2': partner_id.city or None,
                'mmmentdir3': partner_id.state_id.name if partner_id.state_id else partner_id.city or None,
                'mmmentdir4': partner_id.zip or None,
                'mmmacccolcod': picking_id.id
            })

        if type == "move":
            vals.update({
                'mmmartapi': 0,
                'mmmres':None,
                'mmmminudsdis': 1})

        if type == "hueco":
            vals.update({
                'mmmres': None,
                'mmmubidesref': '01P010011',
                'mmmartean': None,
                'mmmmonlot': 1,
                'mmmrecref': 0,
                'mmmartapi': 0,
            })

        if type == "caja":
            vals.update({
                'mmmres': 'FIN',
                'mmmubidesref': '01P010011',
                'mmmartean': None,
                'mmmmonlot': None,
                'mmmrecref': 0,
                'mmmartapi': 0
            })
        return vals