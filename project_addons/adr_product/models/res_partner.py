# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    ##order = "adr_sequence asc"
    adr_sequence = fields.Integer(string="Sequence", default=10)

    @api.multi
    def _get_adr_sequence(self):
        delivery_id = self._context.get('delivery_id', False)
        rpo_ids = self.env['route.partner.order']
        dpo_ids = self.env['delivery.partner.order']
        if dpo_ids:
            for partner_id in self:
                domain = [('partner_id', '=', partner_id.id)]
                rpo_id = rpo_ids.search(domain, limit=1)
                partner_id.adr_sequence = rpo_id and rpo_id.sequence or 10
        else:
             for partner_id in self:
                domain = [('delivery_id', '=', delivery_id), ('partner_id', '=', partner_id.id)]
                dpo_id = dpo_ids.search(domain, limit=1)
                partner_id.adr_sequence = dpo_id and dpo_id.sequence or 10

    adr_sequence = fields.Integer(string="Adr sequence", _compute=_get_adr_sequence)