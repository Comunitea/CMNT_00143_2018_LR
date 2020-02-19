# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from functools import partial
from odoo.tools.misc import formatLang


class StockBatchPicking(models.Model):
    _inherit = "stock.batch.picking"

    valued = fields.Boolean(related="partner_id.valued_picking", readonly=True)
    currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_currency_id",
        string="Currency",
        compute_sudo=True,  # See explanation for sudo in compute method
    )
    amount_untaxed = fields.Monetary(
        compute="_compute_amount_all",
        string="Untaxed Amount",
        compute_sudo=True,  # See explanation for sudo in compute method
    )
    amount_tax = fields.Monetary(
        compute="_compute_amount_all", string="Taxes", compute_sudo=True
    )
    amount_total = fields.Monetary(
        compute="_compute_amount_all", string="Total", compute_sudo=True
    )
    sale_ids = fields.Many2many("sale.order", compute="_compute_sale_ids")
    invoiced = fields.Boolean()

    def _compute_sale_ids(self):
        ##todo revisar Un batch no debería de tener draft move lines una vez validado
        for pick in self:
            pick.sale_ids = pick.mapped("picking_ids.sale_id")

    def _compute_currency_id(self):
        ##todo revisar Un batch no debería de tener draft move lines una vez validado.
        for pick in self:
            sale = pick.mapped("picking_ids.sale_id")
            if not sale:
                pick.currency_id = False
            else:
                pick.currency_id = sale.currency_id.id

    @api.multi
    def _compute_amount_all(self):
        """This is computed with sudo for avoiding problems if you don't have
        access to sales orders (stricter warehouse users, inter-company
        records...).
        """
        for pick in self:
            round_curr = pick.currency_id.round
            amount_tax = 0.0
            for _tax_id, tax_group in pick.get_taxes_values().items():
                amount_tax += round_curr(tax_group["amount"])
            amount_untaxed = sum(
                l.sale_price_subtotal
                for l in (pick.move_line_ids)
            )
            excess_line_vals = pick.get_excess_invoice_line_vals(
                pick.sale_ids[0], get_tax_obj=True
            )
            amount_untaxed += excess_line_vals["price_unit"]

            shipping_line_vals = pick.get_shipping_invoice_line_vals(
                pick.sale_ids[0], get_tax_obj=True
            )
            if shipping_line_vals:
                amount_untaxed += shipping_line_vals["price_unit"]
            pick.update(
                {
                    "amount_untaxed": amount_untaxed,
                    "amount_tax": amount_tax,
                    "amount_total": amount_untaxed + amount_tax,
                }
            )

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        currency = self.currency_id or self.company_id.currency_id
        fmt = partial(
            formatLang,
            self.with_context(lang=self.partner_id.lang).env,
            currency_obj=currency,
        )
        for line in self.move_line_ids:
            if line.sale_line:
                tax_id = line.sale_line.tax_id
            else:
                tax_id = line.move_id._compute_tax_id()

            for tax in tax_id:
                tax_id = tax.id
                if tax_id not in tax_grouped:
                    tax_grouped[tax_id] = {
                        "base": line.sale_price_subtotal,
                        "base_str": fmt(line.sale_price_subtotal),
                        "tax": tax,
                    }
                else:
                    tax_grouped[tax_id]["base"] += line.sale_price_subtotal
        excess_line_vals = self.get_excess_invoice_line_vals(
            self.sale_ids[0], get_tax_obj=True
        )
        for tax in excess_line_vals["invoice_line_tax_ids"]:
            tax_id = tax.id
            if tax_id not in tax_grouped:
                tax_grouped[tax_id] = {
                    "base": excess_line_vals["price_unit"],
                    "base_str": fmt(excess_line_vals["price_unit"]),
                    "tax": tax,
                }
            else:
                tax_grouped[tax_id]["base"] += excess_line_vals["price_unit"]
                tax_grouped[tax_id]["base_str"] = fmt(
                    tax_grouped[tax_id]["base"]
                )
        shipping_line_vals = self.get_shipping_invoice_line_vals(
            self.sale_ids[0], get_tax_obj=True
        )
        if shipping_line_vals:
            for tax in shipping_line_vals["invoice_line_tax_ids"]:
                tax_id = tax.id
                if tax_id not in tax_grouped:
                    tax_grouped[tax_id] = {
                        "base": shipping_line_vals["price_unit"],
                        "base_str": fmt(shipping_line_vals["price_unit"]),
                        "tax": tax,
                    }
                else:
                    tax_grouped[tax_id]["base"] += shipping_line_vals[
                        "price_unit"
                    ]
                    tax_grouped[tax_id]["base_str"] = fmt(
                        tax_grouped[tax_id]["base"]
                    )
        for tax_id, tax_group in tax_grouped.items():
            tax_grouped[tax_id]["amount"] = tax_group["tax"].compute_all(
                tax_group["base"], self.currency_id
            )["taxes"][0]["amount"]
            tax_grouped[tax_id]["amount_str"] = fmt(
                tax_grouped[tax_id]["amount"]
            )
        return tax_grouped

    def _get_invoice_values(self):
        sale = self.sale_ids[0]
        invoice_vals = sale._prepare_invoice()
        # invoice_vals["shipping_type"] = self.shipping_type
        # invoice_vals["financiable_payment"] = sale.financiable_payment
        return invoice_vals

    def get_invoice_line_vals(
        self, order, product, price=False, invoice=False, get_tax_obj=False
    ):
        account = (
            product.property_account_income_id
            or product.categ_id.property_account_income_categ_id
        )
        if not account:
            raise UserError(
                _(
                    'Please define income account for this product: "%s" (id:%d) - or for its category: "%s".'
                )
                % (product.name, product.id, product.categ_id.name)
            )

        fpos = (
            order.fiscal_position_id
            or order.partner_id.property_account_position_id
        )
        if fpos:
            account = fpos.map_account(account)
        line_company_id = self.company_id or order.company_id
        taxes = product.taxes_id.filtered(
            lambda r: not line_company_id or r.company_id == line_company_id
        )
        taxes = (
            fpos.map_tax(taxes, product, order.partner_shipping_id)
            if fpos
            else taxes
        )
        res = {
            "name": product.name,
            "sequence": 99,
            "origin": order.name,
            "account_id": account.id,
            "price_unit": price,
            "quantity": 1,
            "discount": 0,
            "uom_id": product.uom_id.id,
            "product_id": product.id,
            "invoice_line_tax_ids": [(6, 0, taxes.ids)],
            "account_analytic_id": order.analytic_account_id.id,
        }
        if invoice:
            res["invoice_id"] = invoice.id
        if get_tax_obj:
            res["invoice_line_tax_ids"] = taxes
        return res

    def get_excess_invoice_line_vals(
        self, order, invoice=False, get_tax_obj=False
    ):
        price = self.company_id.excess_price
        product = self.env.ref("stock_custom.excess_product")
        return self.get_invoice_line_vals(
            order, product, price, invoice, get_tax_obj
        )

    def get_shipping_invoice_line_vals(
        self, order, invoice=False, get_tax_obj=False
    ):
        shipping_cost_perc = self.company_id.get_shipping_cost_line_percentage(
            self.shipping_type
        )
        if shipping_cost_perc:

            price = sum(
                l.sale_price_unit * (l.qty_done or l.product_qty)
                for l in (self.move_line_ids)
            ) * (shipping_cost_perc / 100)
            product = self.env.ref("stock_custom.shipping_product")
            return self.get_invoice_line_vals(
                order, product, price, invoice, get_tax_obj
            )

    def create_excess_invoice_line(self, order, invoice):
        res = self.get_excess_invoice_line_vals(order, invoice)
        self.env["account.invoice.line"].create(res)

    @api.multi
    def create_invoice(self):
        invoices = self.env["account.invoice"]
        for batch_picking in self:
            invoice_vals = batch_picking._get_invoice_values()
            invoice = self.env["account.invoice"].create(invoice_vals)
            batch_picking.move_lines.create_invoice_line(invoice.id)
            if batch_picking.pack_lines_picking_id:
                batch_picking.pack_lines_picking_id.move_lines.create_invoice_line(
                    invoice.id
                )

            if batch_picking.sale_ids:
                batch_picking.create_excess_invoice_line(
                    batch_picking.sale_ids[0], invoice
                )
                batch_picking.sale_ids.create_service_invoice_lines(invoice)

            invoice.compute_taxes()
            if not invoice.invoice_line_ids:
                raise UserError(_("There is no invoiceable line."))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
                invoice.type = "out_refund"
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice,
            # they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view(
                "mail.message_origin_link",
                values={"self": invoice, "origin": batch_picking.sale_ids},
                subtype_id=self.env.ref("mail.mt_note").id,
            )
            invoices += invoice
            batch_picking.invoiced = True
        return invoices

