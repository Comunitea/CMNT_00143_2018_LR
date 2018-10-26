
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import os
import base64
import glob
import csv


class InvoiceSupplierImportWzd(models.TransientModel):

    _name = 'invoice.supplier.import.wzd'

    path = fields.Char(string='Path')

    @api.model
    def default_get(self, fields):
        res = super(InvoiceSupplierImportWzd, self).default_get(fields)
        param = self.env.ref('virtual_fair.param_import_route')
        res.update({'path': param.value})
        return res

    @api.model
    def _get_import_files(self):
        """
        Return a list with header_file paths, and another list with base files
        """
        header_files = []
        base_files = []
        for file in glob.glob(self.path + "/*.*"):
            file_name = file.split('/')[-1]
            if 'cab' in file_name:
                header_files.append(file)
            elif 'bas' in file_name:
                base_files.append(file)
        return header_files, base_files

    @api.model
    def parse_header_file(self, hfile):
        """
        Return a list o dics, each dic represent a invoice header
        """
        res = []
        f = open(hfile, 'r')
        file_lines = f.read().splitlines()
        for fline in file_lines:
            line = fline.split('\t')
            map_dic = {
                'registro': line[0],
                'tipo_reg': line[1],
                'proveedor': line[2],
                'num_fra': line[3],
                'fecha_fra': line[4],
                'total': line[5],
                'ind_abono': line[6],
                'fec_registro': line[7],
                'fec_contable': line[8],
                'socio': line[9],
                'num_confor': line[10],
                'ind_colab': line[11],
                'forma_pago': line[12],
                'fec_vto': line[13],
                'cia': line[14],
                'dto_pp': line[16],
                'itpf': line[16],
                'ruta': line[17],
            }
            res.append(map_dic)
        return res
    
    @api.model
    def _get_invoice_vals(self, hvals):
        domain = [('ref', '=', hvals['proveedor'])]
        supplier = self.env['res.partner'].search(domain, limit=1)
        invoice_vals = {
            'name': hvals['registro'],
            'partner_id': supplier.id,
            'origin': '',
            'type': 'in_invoice',
            'account_id': supplier.property_account_payable_id.id,
            # # 'journal_id': journal_id,
            # 'currency_id': self.pricelist_id.currency_id.id,
            # 'comment': self.note,
            # 'payment_term_id': self.payment_term_id.id,
            # 'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            # 'company_id': self.company_id.id,
            'user_id': self._uid
            # 'team_id': self.team_id.id
        }
        return invoice_vals
    
    @api.model
    def create_invoices(self, header_vals):
        """
        Return creatred invoices
        """
        inv_pool = self.env['account.invoice']
        res = inv_pool
        for hvals in header_vals:
            vals = self._get_invoice_vals(hvals)
            res += inv_pool.create(vals)
        return res

    @api.model
    def action_view_invoice(self, invoices):
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def import_btn(self):
        # Read files
        header_files, base_files = self._get_import_files()        

        # Get a list of dics with each line values in orther to create
        # from it the invoices
        header_vals = []
        for hfile in header_files:
            header_vals.extend(self.parse_header_file(hfile))

        created_invoices = self.create_invoices(header_vals)

        if created_invoices:
            return self.action_view_invoice(created_invoices)
        return
