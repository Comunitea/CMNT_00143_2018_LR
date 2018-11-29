# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DuplicateInvoiceManualCheckWizard(models.TransientModel):

    _name = 'duplicate.invoice.manual.check.wizard'

    invoices = fields.Many2many('account.invoice')
    has_invoices = fields.Boolean(compute='_compute_has_invoices')

    @api.depends('invoices')
    def _compute_has_invoices(self):
        if self.invoices:
            self.has_invoices = True
        else:
            self.has_invoices = False

    def check_invoices(self):
        for invoice in self.env['account.invoice'].browse(
                self._context.get('active_ids', False)):
            if invoice.check_duplicate_supplier():
                self.invoices += invoice
        return {'type': "ir.actions.do_nothing"}
