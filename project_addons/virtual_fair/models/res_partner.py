
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    property_direct_payment_term_id = fields.Many2one(
        'account.payment.term',
        company_dependent=True,
        string='Alternative Payment Terms (Direct)',
        help="This payment term will be used  if is set instead of configured "
             "when generating Normal Direct Invoices",)


