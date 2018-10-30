
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class ImportationLog(models.Model):

    _name = 'importation.log'

    def _count_invoice(self):
        for log in self:
            log.invoice_count = len(log.invoice_ids)

    name = fields.Char('Name')
    date = fields.Date(string='Date',
                       default=fields.Date.today(),
                       readonly=True)
    invoice_ids = fields.One2many(comodel_name='account.invoice',
                                  inverse_name='log_id', string='Invoices')
    line_ids = fields.One2many(comodel_name='log.line',
                               inverse_name='log_id', string='Log lines')
    invoice_count = fields.Integer(
        string='# of Invoices',
        compute='_count_invoice', readonly=True)
    
    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def create_log_line(self, msg, filename, nline):
        vals = {
            'log_id': self.id,
            'name': msg,
            'filename': filename,
            'nline': nline
        }
        self.env['log.line'].create(vals)


class LogLine(models.Model):
    _name = 'log.line'

    log_id = fields.Many2one('importation.log', string='Log')
    name = fields.Char('Description')

    filename = fields.Char('Filename')
    nline = fields.Integer('Nº line')
