
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import glob


class InvoiceSupplierImportWzd(models.TransientModel):

    _name = 'invoice.supplier.import.wzd'

    name = fields.Char(string='Name')
    path = fields.Char(string='Path')
    log_id = fields.Many2one(comodel_name='importation.log', string='Log')

    @api.model
    def default_get(self, fields):
        """
        Read system parameter to get the path where search for files
        """
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

        if not header_files and not base_files:
            raise UserError(_('Nothing to import'))
        return header_files, base_files

    @api.model
    def check_header_line(self, line, nline, hfile):
        res = False
        if len(line) != 18:
            res = True
        return res

    @api.model
    def parse_header_file(self, hfile):
        """
        Return a list o dics, each dic represent a invoice header
        """
        res = []
        f = open(hfile, 'r')
        file_lines = f.read().splitlines()
        nline = 0
        for fline in file_lines:
            nline += 1
            line = fline.split('\t')

            # CHECK FOR ERRORS IN LINE
            if (self.check_header_line(line, nline, hfile)):
                msg = _('No correct length')
                self.log_id.create_log_line(msg, hfile, nline)
                continue
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
                # for log
                'nline': nline,
                'filename': hfile
            }
            res.append(map_dic)
        return res

    @api.model
    def _format_date(self, oldformat):
        newformat = ''
        if oldformat:
            datetimeobject = datetime.strptime(oldformat, '%Y%m%d')
            newformat = datetimeobject.strftime('%Y-%m-%d')
        return newformat

    @api.model
    def _get_invoice_vals(self, hvals):
        # Get supplier
        supplier_ref = hvals.get('proveedor', False)
        domain = [('ref', '=', supplier_ref)]
        supplier = self.env['res.partner'].search(domain, limit=1)
        if not supplier:
            raise UserError(
                _('Supplier ref %s can not be founded' % supplier_ref))

        # Get type invoice
        type_inv = 'in_invoice'
        if hvals.get('ind_abono', False) == '1':
            type_inv = 'in_refund'

        # Get date invoice
        date_invoice = self._format_date(hvals.get('fecha_fra', False))
        # Get date
        date = self._format_date(hvals.get('fec_contable', False))
        # Get digit_date
        digit_date = self._format_date(hvals.get('fec_registro', False))
        invoice_vals = {
            'partner_id': supplier.id,
            'name': hvals.get('registro', ''),
            'origin': _('Supplier Importation'),
            'type': type_inv,
            'account_id': supplier.property_account_payable_id.id,
            'reference': hvals.get('num_fra', ''),
            'date_invoice': date_invoice,
            'date': date,
            'digit_date': digit_date,
            'num_ass': hvals.get('socio', ''),
            'num_conf': hvals.get('num_confor', ''),
            'featured': True if hvals.get('ind_colab', '') == 'S' else False,
            'user_id': self._uid
            # # 'journal_id':
            # 'currency_id':
            # 'comment':
            # 'payment_term_id':
            # 'fiscal_position_id':
            # 'company_id':
            # 'team_id':
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
    def parse_base_file(self, bfile):
        """
        Return a list o dics, each dic represent a invoice line
        """
        res = []
        f = open(bfile, 'r')
        file_lines = f.read().splitlines()
        nline = 0
        for fline in file_lines:
            nline += 1
            line = fline.split('\t')
            map_dic = {
                'registro': line[0],
                'tipo_reg': line[1],
                'base': line[2],
                'cuota': line[3],
                # for log
                'nline': nline,
                'filename': bfile

            }
            res.append(map_dic)
        return res

    @api.model
    def _get_tax_ids(self, bvals):
        tax_ids = []
        base = float(bvals.get('base', '0.0'))
        tax = float(bvals.get('cuota', '0.0'))
        amount = round((tax / (base or 1.0)) * 100.0, 2)
        domain = [
            ('type_tax_use', '=', 'purchase'),
            ('amount', '=', amount)
        ]
        taxes = self.env['account.tax'].search(domain, limit=1)
        if taxes:
            tax_ids = taxes.ids
        return tax_ids

    @api.model
    def _get_invoice_line_vals(self, bvals, nline):
        invoice_name = bvals.get('registro', '')
        domain = [('name', '=', invoice_name)]
        inv_obj = self.env['account.invoice'].search(domain, limit=1)
        if not inv_obj:
            msg = _('Invoice %s not found' % invoice_name)
            self.log_id.create_log_line(msg, bvals['filename'], bvals['nline'])
            return {}

        # Get account
        cat = self.env['product.category'].search([], limit=1)
        account_id = cat.property_account_expense_categ_id.id
        # TODO: Impuestos
        tax_ids = self._get_tax_ids(bvals)
        line_vals = {
            'name': _('From Supplier Import'),
            'quantity': 1.0,
            'price_unit': bvals.get('base', '1'),
            'account_id': account_id,
            'invoice_id': inv_obj.id,
            'invoice_line_tax_ids': [(6, 0, tax_ids)]
        }
        return line_vals

    @api.model
    def create_invoice_lines(self, base_vals):
        """
        Return creatred invoices
        """
        il_pool = self.env['account.invoice.line']
        res = il_pool
        nline = 0
        for bvals in base_vals:
            nline += 1
            vals = self._get_invoice_line_vals(bvals, nline)
            if vals:
                res += il_pool.create(vals)
        return res
    
    @api.model
    def action_view_import_log(self):
        if self.log_id:
            action = self.env.ref('virtual_fair.action_importation_log').read()[0]
            action['views'] = [
                (self.env.ref('virtual_fair.view_importation_log_form').id,
                    'form')]
            action['res_id'] = self.log_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def import_btn(self):
        # Create importation log record
        log = self.env['importation.log'].create({'name': self.name,
                                                  'date': fields.Date.today()})
        self.log_id = log.id
        # Read files
        header_files, base_files = self._get_import_files()
        # Get a list of dics with each line values in orther to create
        # from it the invoices
        header_vals = []
        for hfile in header_files:
            header_vals.extend(self.parse_header_file(hfile))

        created_invoices = self.create_invoices(header_vals)

        base_vals = []
        for bfile in base_files:
            base_vals.extend(self.parse_base_file(bfile))

        self.create_invoice_lines(base_vals)
        if created_invoices:
            created_invoices.set_fair_conditions()
            self.log_id.write({'invoice_ids': [(6, 0, created_invoices.ids)]})
            return self.action_view_import_log()
        return
