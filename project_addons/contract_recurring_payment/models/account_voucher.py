from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contrato')
    mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate',
        string='Mandato')
    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode',
        string='Mode de pago')

    @api.multi
    def first_move_line_get(self, move_id, company_currency, current_currency):
        res = super(AccountVoucher, self).\
            first_move_line_get(move_id, company_currency, current_currency)
        res.update({
            'payment_mode_id': self.payment_mode_id.id,
            'mandate_id': self.mandate_id.id,
            'partner_bank_id': self.mandate_id.partner_bank_id.id,
            'name': self.number
        })
        return res

    @api.multi
    def account_move_get(self):
        if self.journal_id.sequence_id:
            if not self.journal_id.sequence_id.active:
                raise UserError(
                    _('Please activate the sequence of selected journal !'))
            name = self.journal_id.sequence_id.with_context(
                ir_sequence_date=self.date).next_by_id()
        else:
            raise UserError(_('Please define a sequence on the journal.'))

        move = {
            'name': name,
            'journal_id': self.journal_id.id,
            'narration': self.narration,
            'date': self.account_date,
            'ref': self.reference,
        }
        return move
