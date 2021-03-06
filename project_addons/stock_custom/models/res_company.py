# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.addons.shipping_type.models.info_route_mixin import (
    SHIPPING_TYPE_SEL,
    DEFAULT_SHIPPING_TYPE,
    STRING_SHIPPING_TYPE,
    HELP_SHIPPING_TYPE,
)


class ResCompanyShippingTypePrice(models.Model):

    _name = "res.company.shipping.type.price"

    shipping_type = fields.Selection(
        SHIPPING_TYPE_SEL,
        default=DEFAULT_SHIPPING_TYPE,
        string=STRING_SHIPPING_TYPE,
        help=HELP_SHIPPING_TYPE,
        required=True,
    )
    discount_decrease = fields.Float()
    include_in_lines = fields.Boolean()
    company_id = fields.Many2one("res.company")

    _sql_constraints = [
        (
            "unique_shipping_type",
            "unique (shipping_type, company_id)",
            "Can not configure various prices for a shipping type",
        )
    ]


class ResCompany(models.Model):
    _inherit = "res.company"

    excess_price = fields.Float()
    discount_decrease_financiable = fields.Float(
        "Discount decrease for financed orders"
    )
    discount_decrease_phone = fields.Float(
        "Discount decrease for orders maked by phone"
    )
    shipping_type_price_configuration = fields.One2many(
        "res.company.shipping.type.price", "company_id"
    )
    financiable_account_id = fields.Many2one("account.account")
    phone_account_id = fields.Many2one("account.account")
    shipping_type_account_id = fields.Many2one("account.account")

    def get_discount_decrease_shipping(self, shipping_type):
        price_conf = self.shipping_type_price_configuration.filtered(
            lambda r: r.shipping_type == shipping_type
        )
        if price_conf:
            if not price_conf.include_in_lines:
                return 0
            return price_conf.discount_decrease
        raise UserError(
            _("Shipping type price not configured for {}").format(shipping_type)
        )

    def get_shipping_cost_line_percentage(self, shipping_type):
        if not shipping_type:
            return 0
        price_conf = self.shipping_type_price_configuration.filtered(
            lambda r: r.shipping_type == shipping_type
        )
        if price_conf:
            if price_conf.include_in_lines:
                return 0
            return price_conf.discount_decrease
        raise UserError(
            _("Shipping type price not configured for {}").format(shipping_type)
        )
