# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):


        return super(AccountInvoice, self).action_move_create()


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    num_purchase = fields.Char('Nº Order')
