# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        invoices_no_date = self.filtered(lambda inv: not inv.date and
                                        inv.type in ('in_invoice', 'in_refund'))
        if invoices_no_date:
            invoices_no_date.write({'date': fields.Date.today()})
        return super(AccountInvoice, self).action_move_create()


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    num_purchase = fields.Char('Nº Order')
