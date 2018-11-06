
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    featured_line_ids = fields.One2many(comodel_name='direct.line.section',
                                      inverse_name='company_id',
                                      string='Featured Lines')


class DirectLineSection(models.Model):
    _name = 'direct.line.section'

    company_id = fields.Many2one('res.company', 'Company')
    linf = fields.Float('Inf Limit')
    lsup = fields.Float('Sup Limit')
    percent = fields.Float('Percent (%)')
