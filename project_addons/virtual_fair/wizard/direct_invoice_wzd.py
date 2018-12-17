
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import os
import shutil
import tempfile
import subprocess
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DirectInvoiceWzd(models.TransientModel):

    _name = 'direct.invoice.wzd'

    @api.multi
    def action_view_invoice(self, invoices):
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id,
                               'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def _get_invoice_vals(self, invoices):
        inv = invoices[0]
        vals = {
            'partner_id': inv.associate_id.id,
            'name': '/',
            'origin': ','.join([x.name or '' for x in invoices]),
            'type':
            'out_invoice' if inv.type == 'in_invoice' else 'out_refund',
            'account_id': inv.associate_id.property_account_receivable_id.id,
            # 'reference': reference,
            'date_invoice': fields.Date.today(),
            'user_id': self._uid,
            'from_supplier': True,
        }
        return vals

    @api.model
    def _get_purchase_tax(self, tax):
        tax_ids = []
        domain = [
            ('type_tax_use', '=', 'sale'),
            ('amount', '=', tax.amount)
        ]
        taxes = self.env['account.tax'].search(domain, limit=1)
        if taxes:
            tax_ids = taxes.ids
        return tax_ids

    @api.model
    def _get_line_vals(self, inv, invoices):
        res = []
        group_line_tax = {}
        # Group by tax
        for line in invoices.mapped('invoice_line_ids'):
            tax = line.invoice_line_tax_ids and \
                line.invoice_line_tax_ids[0] or False

            if tax not in group_line_tax:
                group_line_tax[tax] = 0.0
            group_line_tax[tax] += line.price_unit
        # Get account
        cat = self.env['product.category'].search([], limit=1)
        account_id = cat.property_account_income_categ_id.id

        # Create a line for each diferent tax
        for tax in group_line_tax:
            tax_ids = self._get_purchase_tax(tax)
            price_unit = group_line_tax[tax]
            line_vals = {
                'name': _('From Supplier Import'),
                'quantity': 1.0,
                'price_unit': price_unit,
                'account_id': account_id,
                'invoice_id': inv.id,
                'invoice_line_tax_ids': [(6, 0, tax_ids)]
            }
            res.append((0, 0, line_vals))
        return res

    def _copy_images(self, from_invoices, to_invoice):
        sequence = 1

        for invoice in from_invoices:
            attachments = self.env['ir.attachment'].search(
                [('res_id', '=', invoice.id),
                 ('res_model', '=', 'account.invoice')])
            for attachment in attachments:
                new_attachments = self.env['ir.attachment']
                if attachment.name.endswith('.tiff'):
                    tempdir = tempfile.mkdtemp(invoice.number.replace('/', ''))
                    with open(tempdir + '/attachment.tiff', 'wb') as f:
                        f.write(base64.b64decode(attachment.datas))
                    try:
                        from_tiff = tempdir + '/attachment.tiff'
                        to_png = tempdir + '/attachment.png'
                        subprocess.run('convert {} {}'.format(
                            from_tiff, to_png), shell=True)
                    except subprocess.CalledProcessError:
                        raise UserError(_('Error converting tiff to png'))
                    directory = os.listdir(tempdir)
                    directory.sort()
                    for png_file in directory:
                        if png_file.endswith(".png"):
                            with open(tempdir + '/' + png_file, 'rb') as f:
                                new_attachments += new_attachments.create({
                                    'name': png_file,
                                    'type': 'binary',
                                    'datas': base64.b64encode(f.read())
                                })

                    shutil.rmtree(tempdir)
                else:
                    new_attachments = attachment.copy({'res_id': False})
                for new_attachment in new_attachments:
                    self.env['base_multi_image.image'].create({
                        'storage': 'filestore',
                        'attachment_id': new_attachment.id,
                        'owner_model': 'account.invoice',
                        'owner_id': to_invoice.id,
                        'sequence': sequence
                    })
                    sequence += 1


    @api.multi
    def create_invoices(self):
        self.ensure_one()
        invoices = self.env['account.invoice'].\
            browse(self._context.get('active_ids', []))
        inv_grouped = {}

        # Group by associate_id
        for inv in invoices:
            if not inv.associate_id:
                continue
            if inv.associate_id.id not in inv_grouped:
                inv_grouped[inv.associate_id.id] = self.env['account.invoice']
            inv_grouped[inv.associate_id.id] += inv

        created_invoices = self.env['account.invoice']
        for associate_id in inv_grouped:
            # Create Invoice for each associate
            invoice_objs = inv_grouped[associate_id]
            vals = self._get_invoice_vals(invoice_objs)
            inv = self.env['account.invoice'].create(vals)
            self._copy_images(invoice_objs, inv)

            created_invoices += inv
            # Write link between supplier and created invoice
            invoice_objs.write({'customer_invoice_id': inv.id})
            # Create lines
            line_vals = self._get_line_vals(inv, invoice_objs)
            if line_vals:
                inv.write({'invoice_line_ids': line_vals})

        if created_invoices:
            created_invoices.set_fair_supplier_conditions()
            created_invoices.set_featured_line()
            return self.action_view_invoice(created_invoices)
