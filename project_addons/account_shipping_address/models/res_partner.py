# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def _get_partner_mandate(self, company):
        mandates = self.bank_ids.mapped(
                'mandate_ids').filtered(
                lambda x: x.state == 'valid' and x.company_id == company)
        first_valid_mandate_id = mandates.sorted('by_default', reverse=True)[
                                 :1].id
        return first_valid_mandate_id


    @api.multi
    def _compute_valid_mandate_id(self):
        """
            Priorizamos los mandatos del propio partner
            sobre los del commercial_partner_id.
        """
        company_id = self.env.context.get('force_company', False)
        if company_id:
            company = self.env['res.company'].browse(company_id)
        else:
            company = self.env['res.company']._company_default_get(
                'account.banking.mandate')
        for partner in self:
            first_valid_mandate_id = partner._get_partner_mandate(company)
            if not first_valid_mandate_id:
                commercial_partner = partner.commercial_partner_id
                first_valid_mandate_id = commercial_partner._get_partner_mandate(company)
            if first_valid_mandate_id:
                partner.valid_mandate_id = first_valid_mandate_id
