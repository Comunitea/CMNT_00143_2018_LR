# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_partner_mandate(self, company):
        first_valid_mandate_id = False
        if self._context.get('journal_id', False):
            journal = self.env['account.journal'].browse(
                self._context.get('journal_id'))
            first_valid_mandate_id = self.bank_ids.mapped(
                        'mandate_ids').filtered(
                        lambda x: x.state == 'valid' and
                        x.company_id == company and journal in x.journal_ids)
        if not first_valid_mandate_id:
            first_valid_mandate_id = super(
                ResPartner, self)._get_partner_mandate(company)
        return first_valid_mandate_id
