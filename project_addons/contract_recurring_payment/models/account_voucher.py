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
            'partner_bank_id': self.mandate_id.partner_bank_id.id
        })
        return res
