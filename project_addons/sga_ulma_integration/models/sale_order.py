# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_sale_to_ulma(self, batch, ulma_move='', date_expected=''):
        partner_id = self.partner_id
        vals = batch.picking_type_id.get_ulma_vals('sale')
        update_vals = {
            'mmmentdes': '{} ({})'.format(self.partner_id.name, self.name),
            'mmmexpordref': 'N' + self.name,
            'mmmsesid': 1 if batch.picking_type_id.ulma_type == 'SUBUNI' else 2,
            'momcre': "'{}'".format(datetime.datetime.now()),
            'mmmterref': partner_id.ref or None,
            'mmmentdir1': str(partner_id.street) + str(partner_id.street2) or None,
            'mmmentdir2': partner_id.city or None,
            'mmmentdir3': partner_id.state_id.name or None,
            'mmmentdir4': partner_id.zip or None,
            'mmmbatch': batch.name[-9:],
            'mmmacccolcod': batch.id,
            'mmmmomexp': datetime.datetime.strptime(self.effective_date, '%Y-%m-%d'),
            'mmmurgnte': '' if batch.urgent else 'N',
            'mmmtraref': str(batch.shipping_type) + '-N' or None
        }

        vals.update(update_vals)
        return vals