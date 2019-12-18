# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def invoice_line_move_line_get(self):
        # import ipdb; ipdb.set_trace()
        res = super().invoice_line_move_line_get()
        final_data = []
        financiable_account_id = self.company_id.financiable_account_id.id
        phone_account_id = self.company_id.phone_account_id.id
        shipping_type_account_id = self.company_id.shipping_type_account_id.id
        for data in res:
            invl_id = data.get("invl_id")
            line = self.env["account.invoice.line"].browse(invl_id)
            if (
                not line.financiable_decrease
                and not line.shipping_type_decrease
                and not line.phone_decrease
            ):
                final_data.append(data)
                continue
            if not financiable_account_id or not shipping_type_account_id or not phone_account_id:
                raise UserError(
                    _(
                        "The accounts for shipping and financiable costs should be configured"
                    )
                )
            total_price = line.quantity * line.price_unit
            decrease_in_move = 0
            if line.financiable_decrease:
                new_move = data.copy()
                new_move["price"] = total_price * (
                    line.financiable_decrease / 100.0
                )
                new_move["account_id"] = financiable_account_id
                new_move["product_id"] = False
                new_move["name"] = _("financiable cost")
                final_data.append(new_move)
                decrease_in_move += new_move["price"]
            if line.shipping_type_decrease:
                new_move = data.copy()
                new_move["price"] = total_price * (
                    line.shipping_type_decrease / 100.0
                )
                new_move["account_id"] = shipping_type_account_id
                new_move["product_id"] = False
                new_move["name"] = _("Shipping type cost")
                final_data.append(new_move)
                decrease_in_move += new_move["price"]
            if line.phone_decrease:
                new_move = data.copy()
                new_move["price"] = total_price * (
                    line.phone_decrease / 100.0
                )
                new_move["account_id"] = phone_account_id
                new_move["product_id"] = False
                new_move["name"] = _("phone sale cost")
                final_data.append(new_move)
                decrease_in_move += new_move["price"]

            if decrease_in_move:
                final_move = data.copy()
                final_move["price"] = data["price"] - decrease_in_move
                final_data.append(final_move)
        return final_data


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    @api.depends(
        "chained_discount",
        "financiable_decrease",
        "shipping_type_decrease",
        "phone_decrease",
    )
    def _compute_discount(self):
        res = super()._compute_discount()
        for line in self:
            if line.financiable_decrease:
                line.discount -= line.financiable_decrease
            if line.phone_decrease:
                line.discount -= line.phone_decrease
            if line.shipping_type_decrease:
                line.discount -= line.shipping_type_decrease
        return res

    @api.multi
    def _inverse_discount(self):
        return

    discount = fields.Float(
        compute="_compute_discount", inverse=False, readonly=True
    )
    financiable_decrease = fields.Float()
    phone_decrease = fields.Float()
    shipping_type_decrease = fields.Float()
