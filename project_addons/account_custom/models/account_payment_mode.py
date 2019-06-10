# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from datetime import date


class AccountPaymentMode(models.Model):

    _inherit = 'account.payment.mode'

    charge_financed_account_id = fields.Many2one('account.account')
    charge_financed_journal_id = fields.Many2one('account.journal')

    @api.model
    def cron_check_charge_financed_payments(self):
        payment_modes = self.env['account.payment.mode'].search(
            [('charge_financed', '=', True)])
        for payment_mode in payment_modes:
            ctx = self.env.context.copy()
            ctx.update({
                'force_company': payment_mode.company_id.id,
            })
            self = self.with_context(ctx)
            payment_orders = self.env['account.payment.order'].search(
                [('payment_mode_id', '=', payment_mode.id)])
            for payment_order in payment_orders:
                move_line_ids = payment_order.mapped('move_ids.line_ids').ids
                move_lines = self.env['account.move.line'].search(
                    [('id', 'in', move_line_ids),
                     ('debit', '!=', 0),
                     ('date_maturity', '<', date.today()),
                     ('full_reconcile_id', '=', False),
                     ('balance', '!=', 0),
                     ('account_id.reconcile', '=', True)])
                for move_line in move_lines:
                    new_move = self.env['account.move'].create({
                        'ref': payment_order.name,
                        'journal_id': payment_mode.charge_financed_journal_id.id,
                        'company_id': payment_mode.company_id.id,
                    })

                    move_lines = []
                    move_lines.append((
                        0, 0, {
                            'credit': move_line.debit,
                            'account_id': move_line.account_id.id,
                            'partner_id': move_line.partner_id.id,
                        }))
                    move_lines.append((
                        0, 0, {
                            'debit': move_line.debit,
                            'account_id':
                            payment_mode.charge_financed_account_id.id,
                            'partner_id': move_line.partner_id.id,
                        }))
                    new_move.write({'line_ids': move_lines})
                    reconcile_move = new_move.mapped('line_ids').filtered(
                        lambda r: r.credit != 0)
                    (move_line + reconcile_move).reconcile()
