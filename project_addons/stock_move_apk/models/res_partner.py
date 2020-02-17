# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_dict_values(self):
        partner_list= []
        for partner in self:
            partner_obj = {
                'id': partner.id,
                'name': partner.name,
                'shipping_type': partner.shipping_type
            }
            partner_list.append(partner_obj)
        return partner_list
