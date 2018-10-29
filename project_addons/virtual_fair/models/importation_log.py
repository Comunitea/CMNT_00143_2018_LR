
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ImportationLog(models.Model):

    _name = 'importation.log'

    name = fields.Char('Name')
    date = fields.Date(string='Start Date',
                       default=fields.Date.today(),
                       readonly=True)
    line_ids = fields.One2many(comodel_name='log.line',
                               inverse_name='log_id', string='Log lines')


class LogLine(models.Model):
    _name = 'log.line'

    log_id = fields.Many2one('importation.log', string='Log')
    name = fields.Char('Log')
