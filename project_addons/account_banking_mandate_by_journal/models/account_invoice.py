# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def set_mandate(self):
        return super(
            AccountInvoice,
            self.with_context(journal_id=self.journal_id.id)).set_mandate()

    @api.onchange('journal_id')
    def onchange_journal_id_mandate(self):
        self.set_mandate()
