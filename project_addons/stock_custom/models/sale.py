# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class SaleOrderLineDelivery(models.Model):

    _name = 'sale.order.line.delivery'

    line_id = fields.Many2one('sale.order.line')
    quantity = fields.Float()
    delivery_date = fields.Date()


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    def _compute_qty_to_invoice_on_date(self):
        for line in self:
            if self._context.get('invoice_until'):
                deliveries = self.deliveries.filtered(
                    lambda r: r.delivery_date <= self._context.get('invoice_until'))
                if deliveries:
                    qty_delivered_in_date = sum(
                        [x.quantity for x in deliveries])
                    line.qty_to_invoice_on_date = qty_delivered_in_date - line.qty_invoiced
            else:
                line.qty_delivered_in_date = line.qty_delivered - line.qty_invoiced

    def _search_qty_to_invoice_on_date(self, operator, operand):
        if self._context.get('invoice_until'):
            query = """
            SELECT soly.line_id
            FROM sale_order_line_delivery soly
                JOIN sale_order_line sol on soly.line_id = sol.id
            WHERE sol.invoice_status = 'to invoice'
                and sol.company_id = %(company_id)s
                and soly.delivery_date <= %(delivery_date)s
            GROUP BY soly.line_id
            HAVING SUM(soly.quantity) - SUM(sol.qty_invoiced) %(operator)s %(operand)s
            """
            params = {
                'company_id': self.env.user.company_id.id,
                'operator': operator,
                'operand': operand,
                'delivery_date': self._context.get('invoice_until')
            }

            self.env.cr.execute(query, params)
            results = self.env.cr.fetchall()
            if results:
                return[('id', 'in', [x[0] for x in results])]
        else:
            return [('qty_to_invoice', operator, operand)]

    qty_to_invoice_on_date = fields.Float(
        compute='_compute_qty_to_invoice_on_date',
        search='_search_qty_to_invoice_on_date')
    deliveries = fields.One2many('sale.order.line.delivery', 'line_id')


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    invoice_until = fields.Date(
        store=False, search=lambda operator, operand, vals: [])

    def _compute_has_invoiceable_lines(self):
        for order in self:
            if self.env['sale.order.line'].search(
                    [('qty_to_invoice_on_date', '>', 0),
                     ('order_id', '=', order.id)]):
                order.has_invoiceable_lines = True
            else:
                order.has_invoiceable_lines = False

    def _search_has_invoiceable_lines(self, operator, operand):
        if self._context.get('invoice_until'):
            query = """
            SELECT DISTINCT sol.order_id
            FROM sale_order_line_delivery soly
                JOIN sale_order_line sol on soly.line_id = sol.id
            WHERE sol.invoice_status = 'to invoice'
                and sol.company_id = %(company_id)s
                and soly.delivery_date <= %(delivery_date)s
            GROUP BY soly.line_id, sol.order_id
            HAVING SUM(soly.quantity) - SUM(sol.qty_invoiced) > 0
            """
            params = {
                'company_id': self.env.user.company_id.id,
                'delivery_date': self._context.get('invoice_until'),
            }
            self.env.cr.execute(query, params)
            results = self.env.cr.fetchall()
            if results:
                return [('id', 'in', [x[0] for x in results])]
            return [('id', 'in', [])]
        else:
            return [('invoice_status', '=', 'to invoice')]

    has_invoiceable_lines = fields.Boolean(
        compute='_compute_has_invoiceable_lines',
        search='_search_has_invoiceable_lines')

    def action_invoice_create(self, grouped=False, final=False):
        if not hasattr(self, '_get_invoice_group_key'):
            """
            Create the invoice associated to the SO.
            :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                            (partner_invoice_id, currency)
            :param final: if True, refunds will be generated if necessary
            :returns: list of created invoices
            """
            inv_obj = self.env['account.invoice']
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            invoices = {}
            references = {}
            invoices_origin = {}
            invoices_name = {}

            for order in self:
                group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
                for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice_on_date < 0):
                    if float_is_zero(line.qty_to_invoice_on_date, precision_digits=precision):
                        continue
                    if group_key not in invoices:
                        inv_data = order._prepare_invoice()
                        invoice = inv_obj.create(inv_data)
                        references[invoice] = order
                        invoices[group_key] = invoice
                        invoices_origin[group_key] = [invoice.origin]
                        invoices_name[group_key] = [invoice.name]
                    elif group_key in invoices:
                        if order.name not in invoices_origin[group_key]:
                            invoices_origin[group_key].append(order.name)
                        if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                            invoices_name[group_key].append(order.client_order_ref)

                    if line.qty_to_invoice_on_date > 0:
                        line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice_on_date)
                    elif line.qty_to_invoice_on_date < 0 and final:
                        line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice_on_date)

                if references.get(invoices.get(group_key)):
                    if order not in references[invoices[group_key]]:
                        references[invoices[group_key]] |= order

            for group_key in invoices:
                invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
                                        'origin': ', '.join(invoices_origin[group_key])})

            if not invoices:
                raise UserError(_('There is no invoiceable line.'))

            for invoice in invoices.values():
                invoice.compute_taxes()
                if not invoice.invoice_line_ids:
                    raise UserError(_('There is no invoiceable line.'))
                # If invoice is negative, do a refund invoice instead
                if invoice.amount_total < 0:
                    invoice.type = 'out_refund'
                    for line in invoice.invoice_line_ids:
                        line.quantity = -line.quantity
                # Use additional field helper function (for account extensions)
                for line in invoice.invoice_line_ids:
                    line._set_additional_fields(invoice)
                # Necessary to force computation of taxes. In account_invoice, they are triggered
                # by onchanges, which are not triggered when doing a create.
                invoice.compute_taxes()
                invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': references[invoice]},
                    subtype_id=self.env.ref('mail.mt_note').id)
            return [inv.id for inv in invoices.values()]
        invoices = {}
        references = {}

        # START HOOK
        # Take into account draft invoices when creating new ones
        self._get_draft_invoices(invoices, references)
        # END HOOK

        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].\
            precision_get('Product Unit of Measure')

        # START HOOK
        # As now from the beginning there can be invoices related to that
        # order, instead of new invoices, new lines are taking into account in
        # order to know whether there are invoice lines or not
        new_lines = False
        # END HOOK

        for order in self:
            for line in order.order_line.sorted(
                    key=lambda l: l.qty_to_invoice_on_date < 0):
                if float_is_zero(line.qty_to_invoice_on_date,
                                 precision_digits=precision):
                    continue
                # START HOOK
                # Allow to check if a line should not be invoiced
                if line._do_not_invoice():
                    continue
                # END HOOK
                # START HOOK
                # Add more flexibility in grouping key fields
                # WAS: group_key = order.id if grouped
                # else (order.partner_invoice_id.id, order.currency_id.id)
                group_key = order.id if grouped else \
                    self._get_invoice_group_line_key(line)
                # 'invoice' must be always instantiated
                # respecting the old logic
                if group_key in invoices:
                    invoice = invoices[group_key]
                    # END HOOK
                if group_key not in invoices:
                    inv_data = line._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    # START HOOK
                    # This line below is added in order to cover cases where an
                    # invoice is not created and instead a draft one is picked
                    invoice = invoices[group_key]
                    # END HOOK
                    vals = {}
                    if order.name not in invoices[group_key].\
                            origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + \
                            order.name
                    if order.client_order_ref and order.client_order_ref not \
                            in invoices[group_key].name.split(', ') and \
                            order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' +\
                            order.client_order_ref
                    invoices[group_key].write(vals)
                if line.qty_to_invoice_on_date > 0:
                    line.invoice_line_create(invoices[group_key].id,
                                             line.qty_to_invoice_on_date)
                    # START HOOK
                    # Change to true if new lines are added
                    new_lines = True
                    # END HOOK
                elif line.qty_to_invoice_on_date < 0 and final:
                    line.invoice_line_create(invoices[group_key].id,
                                             line.qty_to_invoice_on_date)
                    # START HOOK
                    # Change to true if new lines are added
                    new_lines = True
                    # END HOOOK
                if references.get(invoices.get(group_key)):
                    if order not in references[invoices[group_key]]:
                        references[invoice] = references[invoice] | order

        # START HOOK
        # WAS: if not invoices:
        # Check if new lines have been added in order to determine whether
        # there are invoice lines or not
        if not new_lines and not self.env.context.get('no_check_lines', False):
            raise UserError(_('There is no invoicable line.'))
        # END HOOK

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice,
            # they are triggered by onchanges, which are not triggered when
            # doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view(
                'mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]
