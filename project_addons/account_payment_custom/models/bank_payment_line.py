# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    def domain_journal_id(self):
        if not self.payment_mode_id:
            return [('type', '=', 'bank')]
        if self.payment_mode_id.bank_account_link == 'fixed':
            return [('id', '=', self.payment_mode_id.fixed_journal_id.id)]
        elif self.payment_mode_id.bank_account_link == 'variable':
            jrl_ids = self.payment_mode_id.variable_journal_ids.ids
            return [('id', 'in', jrl_ids)]

    journal_id = fields.Many2one('account.journal', 'Journal',
                                 domain=domain_journal_id)
    payment_mode_id = fields.Many2one('account.payment.mode', 'Payment mode')
    date = fields.Date(store=True)
    def get_group_key(self):
        return (self.journal_id.id, self.payment_mode_id.id)
