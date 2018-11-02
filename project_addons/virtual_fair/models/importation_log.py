
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class ImportationLog(models.Model):

    _name = 'importation.log'

    def _count_invoice(self):
        for log in self:
            log.invoice_count = len(log.invoice_ids)

    def _error_exist(self):
        for log in self:
            if log.hline_ids:
                log.header_errors = True
            if log.bline_ids:
                log.base_errors = True
            log.invoice_count = len(log.invoice_ids)

    name = fields.Char('Name')
    date = fields.Date(string='Date',
                       default=fields.Date.today(),
                       readonly=True)
    invoice_ids = fields.One2many(comodel_name='account.invoice',
                                  inverse_name='log_id', string='Invoices')
    hline_ids = fields.One2many(comodel_name='log.line',
                                inverse_name='log_id',
                                string='Errors',
                                domain=[('type', '=', 'cab')])
    bline_ids = fields.One2many(comodel_name='log.line',
                                inverse_name='log_id',
                                string='Errors',
                                domain=[('type', '=', 'bas')])
    invoice_count = fields.Integer(
        string='# of Invoices',
        compute='_count_invoice', readonly=True)
    header_errors = fields.Boolean('Header error', compute='_error_exist')
    base_errors = fields.Boolean('Base error', compute='_error_exist')

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_in_refund').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [
                (self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def create_log_line(self, msg, values, invoice_id=False):
        vals = {
            'log_id': self.id,
            'name': msg,
            'type': values.get('type', 'bas'),
            'filename': values.get('filename', ''),
            'nline': values.get('nline', 0),
            'invoice_id': invoice_id
        }
        self.env['log.line'].create(vals)


class LogLine(models.Model):
    _name = 'log.line'

    log_id = fields.Many2one('importation.log', string='Log')
    type = fields.Selection([('cab', 'Headers'), ('bas', 'Base')], 'File type')
    name = fields.Char('Description')
    filename = fields.Char('File')
    nline = fields.Integer('Nº line')
    invoice_id = fields.Many2one(comodel_name='account.invoice',
                                 string='Invoice')
