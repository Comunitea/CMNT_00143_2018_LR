# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
import glob


class InvoiceSupplierImportWzd(models.TransientModel):

    _name = 'invoice.supplier.import.wzd'

    name = fields.Char()
    path = fields.Char()
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
        """
        Check for correct length
        """
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
        with open(hfile, 'r') as f:
            file_lines = f.read().splitlines()
            nline = 0
            for fline in file_lines:
                nline += 1
                line = fline.split('\t')

                # CHECK FOR ERRORS IN LINE
                if (self.check_header_line(line, nline, hfile)):
                    msg = _('No correct length')
                    hvals = {
                        'nline': nline,
                        'filename': hfile,
                        'type': 'cab',
                    }
                    self.log_id.create_log_line(msg, hvals)
                    continue
                map_dic = {
                    'registro': line[0],
                    # 'tipo_reg': line[1],
                    'proveedor': line[2],
                    'num_fra': line[3],
                    'fecha_fra': line[4],
                    # 'total': line[5],
                    'ind_abono': line[6],
                    'fec_registro': line[7],
                    'fec_contable': line[8],
                    'socio': line[9],
                    'num_confor': line[10],
                    'ind_colab': line[11],
                    # 'forma_pago': line[12],
                    # 'fec_vto': line[13],
                    # 'cia': line[14],
                    # 'dto_pp': line[16],
                    # 'itpf': line[16],
                    'ruta': line[17],
                    # for log
                    'nline': nline,
                    'filename': hfile,
                    'type': 'cab',
                }
                res.append(map_dic)
        return res

    @api.model
    def _format_date(self, oldformat):
        newformat = ''
        if oldformat:
            datetimeobject = datetime.strptime(oldformat, '%Y%m%d')
            newformat = fields.Date.to_string(datetimeobject)
        return newformat

    @api.model
    def _get_invoice_vals(self, hvals):
        # Find exisating invoice
        reference = hvals.get('num_fra', '')
        # Get supplier
        supplier_ref = hvals.get('proveedor', False)
        supplier = False
        if supplier_ref:
            domain = [('id_prov', '=', int(supplier_ref))]
        supplier = self.env['res.partner'].search(domain, limit=1)
        if not supplier:
            msg = _('Supplier identifier %s could not be founded') %\
                supplier_ref
            self.log_id.create_log_line(msg, hvals)
            return {}

        # Get type invoice
        type_inv = 'in_invoice'
        if hvals.get('ind_abono', False) == '0':
            type_inv = 'in_refund'

        # Get date invoice
        date_invoice = self._format_date(hvals.get('fecha_fra', False))
        if fields.Date.from_string(date_invoice) > date.today():
            msg = _('Invoice date is after today')
            self.log_id.create_log_line(msg, hvals)
            return {}
        # Get date
        date_ = self._format_date(hvals.get('fec_contable', False))
        # Get digit_date
        digit_date = self._format_date(hvals.get('fec_registro', False))
        # Get associate
        associate_id = False
        num_ass = hvals.get('socio', '')
        if num_ass:
            domain = [('ref', '=', num_ass), ('customer', '=', True)]
            p = self.env['res.partner'].search(domain, limit=1)
            associate_id = p.id if p else False
        # featured = True if hvals.get('ind_colab', '') == 'S' else False
        featured = True if associate_id else False
        invoice_vals = {
            'partner_id': supplier.id,
            'name': hvals.get('registro', ''),
            'tag': hvals.get('registro', ''),
            'origin': _('Supplier Importation'),
            'type': type_inv,
            'account_id': supplier.property_account_payable_id.id,
            'reference': reference,
            'date_invoice': date_invoice,
            'date': date_,
            'digit_date': digit_date,
            'num_ass': num_ass,
            'associate_id': associate_id,
            'num_conf': hvals.get('num_confor', ''),
            'featured': featured,
            'user_id': self._uid,
            'from_import': True,
            # # 'journal_id':
            # 'currency_id':
            # 'comment':
            # 'payment_term_id':
            # 'fiscal_position_id':
            # 'company_id':
            # 'team_id':
        }
        return invoice_vals

    def _create_attachment(self, image_route, invoice):
        with open(image_route, 'rb') as image_file:
            b64_image = base64.b64encode(image_file.read())
            attachment = self.env['ir.attachment'].create({
                'res_model': 'account.invoice',
                'res_id': invoice.id,
                'name': image_route.split('/')[-1],
                'datas': b64_image,
                'datas_fname': image_route.split('/')[-1],
                })


    @api.model
    def create_invoices(self, header_vals):
        """
        Return creatred invoices
        """
        inv_pool = self.env['account.invoice']
        res = inv_pool
        for hvals in header_vals:
            vals = self._get_invoice_vals(hvals)
            if vals:
                new_invoice = inv_pool.create(vals)
                res += new_invoice
                invoice_date = fields.Date.from_string(
                    new_invoice.date_invoice)
                if invoice_date + timedelta(days=365) < date.today():
                    msg = _('Invoice date has more than 365 days')
                    self.log_id.create_log_line(msg, hvals, new_invoice.id)
                if new_invoice.check_duplicate_supplier():
                    msg = _(
                        'The invoice from supplier %s and number %s \
                        alredery exists') % \
                        (new_invoice.partner_id.name,
                         new_invoice.clean_reference)
                    self.log_id.create_log_line(msg, hvals, new_invoice.id)

                if hvals.get('ruta') and new_invoice:
                    self._create_attachment(hvals.get('ruta'), new_invoice)
        return res

    @api.model
    def check_base_line(self, line, nline):
        res = False
        if len(line) != 4:
            res = True
        return res

    @api.model
    def parse_base_file(self, bfile):
        """
        Return a list o dics, each dic represent a invoice line
        """
        res = []
        with open(bfile, 'r') as f:
            file_lines = f.read().splitlines()
            nline = 0
            for fline in file_lines:
                nline += 1
                line = fline.split('\t')

                # CHECK FOR ERRORS IN LINE
                if (self.check_base_line(line, nline)):
                    msg = _('No correct length')
                    hvals = {
                        'nline': nline,
                        'filename': bfile,
                        'type': 'cab',
                    }
                    self.log_id.create_log_line(msg, hvals)
                    continue

                map_dic = {
                    'registro': line[0],
                    'tipo_reg': line[1],
                    'base': line[2],
                    'cuota': line[3],
                    # for log
                    'nline': nline,
                    'filename': bfile,
                    'type': 'bas'

                }
                res.append(map_dic)
        return res

    @api.model
    def _get_tax_ids(self, bvals):
        tax_ids = []
        base = float(bvals.get('base', '0.0'))
        tax = float(bvals.get('cuota', '0.0'))
        amount = int(round((tax / (base or 1.0)) * 100.0, 0))
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
            msg = _('Invoice %s not found') % invoice_name
            self.log_id.create_log_line(msg, bvals)
            return {}

        # Get account
        cat = self.env['product.category'].search([], limit=1)
        account_id = cat.property_account_expense_categ_id.id

        # Get taxes
        tax_ids = self._get_tax_ids(bvals)
        if not tax_ids:
            msg = _('No tax founded.')
            self.log_id.create_log_line(msg, bvals, inv_obj.id)
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
            action = self.env.ref('virtual_fair.action_importation_log').\
                read()[0]
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
            created_invoices.set_fair_supplier_conditions()
            created_invoices.set_supplier_featured_percent()
            self.log_id.write({'invoice_ids': [(6, 0, created_invoices.ids)]})
        return self.action_view_import_log()
