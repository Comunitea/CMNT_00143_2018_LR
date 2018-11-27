# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class BankPaymentLineSetJournal(models.TransientModel):
    _name = 'bank.payment.line.set.journal'

    journal_id = fields.Many2one('account.journal', 'Journal')
    payment_mode_id = fields.Many2one('account.payment.mode', 'Payment mode')

    def domain_journal_id(self):
        if not self.payment_mode_id:
            return [('type', '=', 'bank')]
        if self.payment_mode_id.bank_account_link == 'fixed':
            return [('id', '=', self.payment_mode_id.fixed_journal_id.id)]
        elif self.payment_mode_id.bank_account_link == 'variable':
            jrl_ids = self.payment_mode_id.variable_journal_ids.ids
            return [('id', 'in', jrl_ids)]

    @api.onchange('payment_mode_id')
    def payment_mode_id_change(self):
        domain = self.domain_journal_id()
        res = {'domain': {
            'journal_id': domain
        }}
        journals = self.env['account.journal'].search(domain)
        if len(journals) == 1:
            self.journal_id = journals
        if self.payment_mode_id.default_date_prefered:
            self.date_prefered = self.payment_mode_id.default_date_prefered
        return res

    def set_data(self):
        self.env['bank.payment.line'].browse(
            self._context.get('active_ids', False)).write(
                {'journal_id': self.journal_id.id,
                 'payment_mode_id': self.payment_mode_id.id})
