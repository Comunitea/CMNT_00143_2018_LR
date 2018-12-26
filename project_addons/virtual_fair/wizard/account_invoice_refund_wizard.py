# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    featured_error = fields.Boolean()
    new_featured_percentage = fields.Float()

    def invoice_refund(self):
        # Calculamos la diferencia de featured y la pasamos en contexto
        new_featured_price = 0.0
        if self.filter_refund != 'refund':
            self.featured_error = False
        if self.featured_error:
            invoice = self.env['account.invoice'].browse(
                self._context.get('active_id', False))
            featured_product_id = self.env.ref(
                'virtual_fair.featured_product').id
            featured_lines_price = sum(invoice.invoice_line_ids.filtered(
                lambda r: r.product_id.id == featured_product_id).mapped(
                    'price_total'))
            if not featured_lines_price:
                raise UserError(_('Featured line not found'))
            total_without_featured = invoice.amount_total - \
                featured_lines_price
            new_featured_price = total_without_featured * \
                (self.new_featured_percentage / 100.0)
            new_featured_price = featured_lines_price - new_featured_price
        return super(
            AccountInvoiceRefund,
            self.with_context(
                featured_error=self.featured_error,
                new_featured_price=new_featured_price)
                ).invoice_refund()
