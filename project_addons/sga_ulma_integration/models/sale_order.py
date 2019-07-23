# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'



    def get_sale_to_ulma(self, pick, ulma_move, date_expected):
        partner_id = self.partner_id
        vals = pick.picking_type_id.get_ulma_vals('sale')
        update_vals = {
            'mmmacccolcod': self.id,
            'mmmentdes': '{} ({})'.format(self.partner_id.name, self.name),
            'mmmexpordref': 'N' + self.name,
            'mmmsesid': 2,
            'momcre': ulma_move.momcre,
            'mmmterref': partner_id.ref,
            'mmmentdir1': str(partner_id.street) + str(partner_id.street2),
            'mmmentdir2': partner_id.city,
            'mmmentdir3': partner_id.state_id.name,
            'mmmentdir4': partner_id.zip,
            'mmmbatch': pick.id,
            'mmmmomexp': date_expected,
            'mmmurgnte': '' if pick.urgent else 'N',
            'mmmtraref': str(pick.shipping_type) + '-N'
            }

        vals.update(update_vals)
        return vals