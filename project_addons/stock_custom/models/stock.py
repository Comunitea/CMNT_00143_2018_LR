# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields
from datetime import date


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.model
    def _compute_tax_id(self):
        ##compia de la linea de sale order line para el movimiento

        if self.sale_line_id:

            line = self.sale_line_id
            fpos = (
                line.order_id.fiscal_position_id
                or line.order_id.partner_id.property_account_position_id
            )
            # If company_id is set, always filter taxes by the company
            line_company_id = line.company_id or line.order_id.company_id
            taxes = line.product_id.taxes_id.filtered(
                lambda r: not line_company_id or r.company_id == line_company_id
            )
            tax_id = (
                fpos.map_tax(
                    taxes, line.product_id, line.order_id.partner_shipping_id
                )
                if fpos
                else taxes
            )

        else:
            comercial_partner_id = self.partner_id.commercial_partner_id
            fpos = comercial_partner_id.property_account_position_id
            line_company_id = self.company_id or self.order_id.company_id
            taxes = self.product_id.taxes_id.filtered(
                lambda r: not line_company_id or r.company_id == line_company_id
            )
            tax_id = (
                fpos.map_tax(taxes, self.product_id, self.partner_id)
                if fpos
                else taxes
            )
        return tax_id

    @api.multi
    def create_invoice_line(self, invoice_id):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        lines = []
        for move in self:
            if move.sale_line_id:
                invoice_line_vals = move.sale_line_id._prepare_invoice_line(
                    move.quantity_done
                )
            else:
                # Son palets
                invoice_line_vals = move._prepare_invoice_line()

            vals = {"invoice_id": invoice_id}
            if move.sale_line_id:
                vals.update(
                    {
                        "sale_line_ids": [(6, 0, [move.sale_line_id.id])],
                        "shipping_type_decrease": move.company_id.get_discount_decrease_shipping(
                            move.shipping_type
                        ),
                    }
                )
                if move.sale_line_id.order_id.financiable_payment:
                    vals[
                        "financiable_decrease"
                    ] = move.company_id.discount_decrease_financiable
                if move.sale_line_id.order_id.phone_order:
                    vals[
                        "phone_decrease"
                    ] = move.company_id.discount_decrease_phone
            invoice_line_vals.update(vals)
            lines.append(
                self.env["account.invoice.line"].create(invoice_line_vals)
            )
        return lines

    @api.multi
    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for move line if not sale_order_line

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = (
            self.product_id.property_account_income_id
            or self.product_id.categ_id.property_account_income_categ_id
        )
        fpos = (
            self.partner_id.commercial_partner_id.property_account_position_id
        )
        if fpos:
            account = fpos.map_account(account)
        res = {
            "name": self.name,
            "sequence": self.sequence,
            "origin": self.picking_id.orig_batch_picking_id.order_id.name,
            "account_id": account.id,
            "price_unit": self.product_id.lst_price,
            "quantity": self.quantity_done,
            "discount": 0,
            "uom_id": self.product_uom.id,
            "product_id": self.product_id.id or False,
            "layout_category_id": False,
            "invoice_line_tax_ids": [(6, 0, self._compute_tax_id().ids)],
        }
        return res


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    computed_discount = fields.Float(compute="_compute_computed_discount")

    def _compute_computed_discount(self):

        for line in self.filtered(lambda x: x.sale_line):
            discount = line.sale_discount
            discount -= line.move_id.company_id.get_discount_decrease_shipping(
                line.move_id.shipping_type
                or line.batch_picking_id.shipping_type
            )
            if line.sale_line.order_id.financiable_payment:
                discount -= (
                    line.move_id.company_id.discount_decrease_financiable
                )
            if line.sale_line.order_id.phone_order:
                discount -= line.move_id.company_id.discount_decrease_phone
            line.computed_discount = discount

    @api.multi
    def _compute_sale_order_line_fields(self):
        """This is computed with sudo for avoiding problems if you don't have
        access to sales orders (stricter warehouse users, inter-company
        records...).
        """
        sale_lines = self.filtered(lambda x: x.sale_line)
        no_sale_lines = self - sale_lines
        for line in sale_lines:
            discount = line.computed_discount
            sale_line = line.sale_line
            price_unit = line.sale_price_unit * (1 - (discount or 0.0) / 100.0)
            taxes = line.sale_tax_id.compute_all(
                price_unit=price_unit,
                currency=line.currency_id,
                quantity=line.qty_done or line.product_qty,
                product=line.product_id,
                partner=sale_line.order_id.partner_shipping_id,
            )
            if sale_line.company_id.tax_calculation_rounding_method == (
                "round_globally"
            ):
                price_tax = sum(
                    t.get("amount", 0.0) for t in taxes.get("taxes", [])
                )
            else:
                price_tax = taxes["total_included"] - taxes["total_excluded"]
            line.update(
                {
                    "sale_tax_description": ", ".join(
                        t.name or t.description for t in line.sale_tax_id
                    ),
                    "sale_price_subtotal": taxes["total_excluded"],
                    "sale_price_tax": price_tax,
                    "sale_price_total": taxes["total_included"],
                }
            )

        for line in no_sale_lines:
            discount = 0
            price_unit = line.product_id.lst_price
            move_tax_id = line.move_id._compute_tax_id()
            taxes = move_tax_id.compute_all(
                price_unit=price_unit,
                currency=line.partner_id.commercial_partner_id.currency_id,
                quantity=line.qty_done or line.product_qty,
                product=line.product_id,
                partner=line.partner_id,
            )
            if line.move_id.company_id.tax_calculation_rounding_method == (
                "round_globally"
            ):
                price_tax = sum(
                    t.get("amount", 0.0) for t in taxes.get("taxes", [])
                )
            else:
                price_tax = taxes["total_included"] - taxes["total_excluded"]
            line.update(
                {
                    "sale_tax_description": ", ".join(
                        t.name or t.description for t in move_tax_id
                    ),
                    "sale_price_subtotal": taxes["total_excluded"],
                    "sale_price_tax": price_tax,
                    "sale_price_total": taxes["total_included"],
                }
            )
