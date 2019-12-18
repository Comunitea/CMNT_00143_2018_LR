# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    phone_account_id = fields.Many2one(
        "account.account",
        related="company_id.phone_account_id",
        string="Account for financiable charge",
        domain="[('company_id', '=', company_id)]",
    )

    financiable_account_id = fields.Many2one(
        "account.account",
        related="company_id.financiable_account_id",
        string="Account for financiable charge",
        domain="[('company_id', '=', company_id)]",
    )

    shipping_type_account_id = fields.Many2one(
        "account.account",
        related="company_id.shipping_type_account_id",
        string="Account for shipping type charge",
        domain="[('company_id', '=', company_id)]",
    )
