# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'


    @api.multi
    def action_move_create(self):
        account_move_line = self.env['account.move.line']
        for inv in self:
            ml_ids=[]
            if inv.type == 'out_invoice':
                ml_ids = account_move_line.search([('partner_id', '=',
                                               inv.commercial_partner_id.id),
                                               ('date', '=', inv.date_invoice),
                                               ('debit', '=',
                                                inv.amount_total )
                                               ])
            if inv.type == 'out_refund':
                ml_ids = account_move_line.search([('partner_id', '=',
                                                    inv.commercial_partner_id.id),
                                                   ('date', '=',
                                                    inv.date_invoice),
                                                   ('credit', '=',
                                                    inv.amount_total)
                                                   ])
            if ml_ids:
                ml_ids.mapped('move_id').unlink()

        return super(AccountInvoice, self).action_move_create()
