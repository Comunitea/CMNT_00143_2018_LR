# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from io import BytesIO
import base64


class AccountInvoiceImportWizard(models.TransientModel):
    _name = 'account.invoice.import.wizard'

    input_file = fields.Binary()

    def process_updates(self, vals, model):
        specs = self.env[model]._onchange_spec()
        updates = self.env[model].onchange(vals, [], specs)
        value = updates.get('value', {})
        for name, val in value.items():
            if isinstance(val, tuple):
                value[name] = val[0]
            if name not in vals.keys():
                vals[name] = value[name]
        return vals

    def _get_taxes(self, tax_eids):
        taxes = self.env['account.tax']
        for tax_eid in tax_eids.split(','):
            taxes += self.env.ref(tax_eid)
        return taxes

    def process_file(self):
        tree = etree.parse(BytesIO(base64.b64decode(self.input_file)))
        root_element = tree.getroot()
        journal = self.env.ref(root_element.attrib['idSr'])
        invoice_ids = []
        for invoice_data in root_element.iter('PA'):
            purchase_number = invoice_data.attrib['num']
            partners = invoice_data.find('partes')
            customer_tag = partners.find('cliente')
            customer_ref = customer_tag.attrib['refInt']
            customer = self.env['res.partner'].search(
                [('ref', '=', customer_ref), ('customer', '=', True)])
            if not customer:
                raise ValidationError(
                    _('Customer with reference {} not exists').format(
                        customer_ref))
            payment_term_eid = customer_tag.find('plazo').attrib['id']
            fiscal_position_eid = customer_tag.find('RegIVA').text
            invoice_vals = {
                'partner_id': customer.id,
                'journal_id': journal.id,
                'payment_term_id': self.env.ref(payment_term_eid).id,
                'fiscal_position_id': self.env.ref(fiscal_position_eid).id,
                'type': 'out_invoice',
            }

            invoice_vals = self.process_updates(invoice_vals,
                                                'account.invoice')
            invoice = self.env['account.invoice'].create(invoice_vals)
            invoice_ids.append(invoice.id)

            for line in invoice_data.find('articulos').iter('articulo'):
                line_data = line.find('datosVenta')
                taxes = self._get_taxes(line_data.find('tipoIVA').attrib['id'])
                line_vals = {
                    'name': line.find('referencia').text + ' - ' +
                    line.find('nombre').text,
                    'quantity': float(line_data.find('unidades').text),
                    'price_unit': float(line_data.find('precioUnitario').text),
                    'invoice_line_tax_ids': [(4, x.id) for x in taxes],
                    'num_purchase': purchase_number,
                    'invoice_id': invoice.id
                }
                line_vals = self.process_updates(line_vals,
                                                 'account.invoice.line')
                self.env['account.invoice.line'].with_context(
                    journal_id=journal.id, type='out_invoice').create(
                        line_vals)
            delivery_data = customer_tag.find('porteVenta')
            taxes = self._get_taxes(delivery_data.find('tipoIVAPorte').attrib['id'])
            delivery_percentage = float(delivery_data.find('pct').text)
            delivery_product = self.env['product.product'].search([(
                'default_code', '=', 'PORTE')])
            delivery_vals = {
                'name': _('Delivery'),
                'quantity': 1,
                'invoice_line_tax_ids': [(4, x.id) for x in taxes],
                'num_purchase': purchase_number,
                'price_unit': invoice.amount_untaxed *
                (delivery_percentage / 100),
                'invoice_id': invoice.id,
                'product_id': delivery_product and delivery_product.id or False
            }
            if delivery_vals['price_unit']:
                delivery_vals = self.process_updates(delivery_vals,
                                                    'account.invoice.line')
                self.env['account.invoice.line'].with_context(
                    journal_id=journal.id, type='out_invoice').create(
                        delivery_vals)
            invoice.compute_taxes()
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoice_ids) == 0:
            raise UserError(_('No invoice was created'))
        elif len(invoice_ids) > 1:
            action['domain'] = [('id', 'in', invoice_ids)]
        elif len(invoice_ids) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id,
                                'form')]
            action['res_id'] = invoice_ids[0]
        return action
