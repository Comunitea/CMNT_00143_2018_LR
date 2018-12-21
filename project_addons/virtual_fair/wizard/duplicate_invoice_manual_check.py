# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DuplicateInvoiceManualCheckWizard(models.TransientModel):

    _name = 'duplicate.invoice.manual.check.wizard'

    invoice_lines = fields.One2many('duplicate.invoice.manual.check.wizard.line', 'wizard')
    has_invoices = fields.Boolean(compute='_compute_has_invoices')
    check_different_name = fields.Boolean(
        'Search invoices with different number')

    @api.depends('invoice_lines')
    def _compute_has_invoices(self):
        if self.invoice_lines:
            self.has_invoices = True
        else:
            self.has_invoices = False

    def check_invoices(self):
        for invoice in self.env['account.invoice'].browse(
                self._context.get('active_ids', False)):
            duplicate = invoice.with_context(check_different_name=self.check_different_name).check_duplicate_supplier()
            duplicate_history = invoice.with_context(check_different_name=self.check_different_name).check_duplicate_history()
            if duplicate or duplicate_history:
                self.env['duplicate.invoice.manual.check.wizard.line'].create({
                    'wizard': self.id,
                    'orig_invoice': invoice.id,
                    'duplicate_invoices': [(6, 0, [x.id for x in duplicate])],
                    'duplicate_invoices_history': [(6, 0, [x.id for x in duplicate_history])],
                })
        return {'type': "ir.actions.do_nothing"}


class DuplicateInvoiceManualCheckWizardLine(models.TransientModel):

    _name = 'duplicate.invoice.manual.check.wizard.line'

    wizard = fields.Many2one('duplicate.invoice.manual.check.wizard')
    orig_invoice = fields.Many2one('account.invoice')
    duplicate_invoices = fields.Many2many('account.invoice', relation='duplicate_wizard_line_invoice_rel')
    duplicate_invoices_history = fields.Many2many('account.invoice.history', relation='duplicate_wizard_line_invoice_history_rel')
