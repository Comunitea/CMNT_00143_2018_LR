# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    country_id = fields.Many2one(related='partner_id.country_id', store=True,
                                 string='Partner Country')
    #account_position_id = fields.Many2one(
    #    related='partner_id.property_account_position_id',
    #                                store=True, string='Partner Position')
