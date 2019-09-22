
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import UserError
import base64


class VirtualFairImportWzd(models.TransientModel):

    _name = 'virtual.fair.import.wzd'

    file = fields.Binary(string='File', required=True)
    fair_filename = fields.Char(string='Fair Filename')

    @api.model
    def _get_partner_id_by_ref(self, ref):
        res = False
        if ref:
            domain = [('ref', '=', ref)]
            partner = self.env['res.partner'].search(domain, limit=1)
            if partner:
                res = partner.id
        return res

    @api.model
    def _get_term_id_by_name(self, term_name):
        res = False
        if term_name:
            domain = [('name', '=', term_name)]
            term = self.env['account.payment.term'].search(domain, limit=1)
            if term:
                res = term.id
        return res

    @api.model
    def _str2float(self, str):
        return str.replace('.', '').replace(',', '.')

    @api.model
    def _get_header_vals(self, xml_root):
        return {
            'name': xml_root.text,
            'id_name': xml_root.get('id'),
            'date_start': xml_root.get('fDesde'),
            'date_end': xml_root.get('fHasta'),
        }

    @api.model
    def _get_customer_line_vals(self, xml_root):
        res = []
        for cust in xml_root.find('Clientes').iterchildren():
            # Get partner
            ref = cust.get('refInt')
            customer_id = self._get_partner_id_by_ref(ref)

            # Get payment term
            term_name = cust.text
            term_id = self._get_term_id_by_name(term_name)

            # Set vals
            vals = {
                'facturation': cust.get('facturacion'),
                'ref_int': cust.get('refInt') or _('**ALL**'),
                'customer_type': cust.get('tipoCliente'),
                'condition_type': cust.get('tipoCondicion') or
                _('**BY_CONDITIONS**'),
                'value': term_name,
                'customer_id': customer_id,
                'term_id': term_id,
            }
            res.append((0, 0, vals))
        return res

    @api.model
    def _get_section_vals(self, cond):
        res = []
        if cond.find('Tramo') is None:
            return res
        for sect in cond.iterchildren():
            term_name = sect.text
            term_id = self._get_term_id_by_name(term_name)
            vals = {
                'ean': sect.get('ean'),
                'linf': self._str2float(sect.get('lInf')),
                'lsup': self._str2float(sect.get('lSup')),
                'value': term_name,
                'term_id': term_id
            }
            res.append((0, 0, vals))
        return res

    @api.model
    def _get_condition_vals(self, supp):
        res = []
        if supp.find('condicion') is None:
            return res
        for cond in supp.iterchildren():
            section_vals = self._get_section_vals(cond)
            vals = {
                'facturation': cond.get('facturacion'),
                'condition_type': cond.get('tipoCondicion'),
                'section_ids': section_vals
            }
            res.append((0, 0, vals))
        return res

    @api.model
    def _get_supplier_line_vals(self, xml_root):
        res = []
        for supp in xml_root.find('Proveedores').iterchildren():
            condition_vals = self._get_condition_vals(supp)

            ref = supp.get('refInt')
            supplier_id = self._get_partner_id_by_ref(ref)

            vals = {
                'ref_int': ref or _('**ALL**'),
                'condition_ids': condition_vals,
                'facturation': supp.get('facturacion'),
                'condition_type': supp.get('tipoCondicion') or
                _('**BY_CONDITIONS**'),
                'value': supp.text,
                'supplier_id': supplier_id,
            }
            res.append((0, 0, vals))
        return res

    @api.multi
    def import_fair(self):
        self.ensure_one()

        # Read Xml File
        vf_pool = self.env['virtual.fair']
        file_data = base64.b64decode(self.file)
        try:
            xml_root = etree.fromstring(file_data)
        except Exception as e:
            raise UserError(_(
                    "This XML file is not XML-compliant. Error: %s") % e)

        # If already imported unlink old fair
        exist_fairs = vf_pool.search([('id_name', '=', xml_root.get('id'))])
        if exist_fairs:
            exist_fairs.unlink()

        # Create fair model
        vals = self._get_header_vals(xml_root)
        fair = vf_pool.create(vals)

        # Creating related customers
        line_vals = self._get_customer_line_vals(xml_root)
        if line_vals:
            fair.write({'customer_ids': line_vals})

        # Creating related suppliers
        line_vals = []
        line_vals = self._get_supplier_line_vals(xml_root)
        if line_vals:
            fair.write({'supplier_ids': line_vals})

        # Open Form View
        if fair:
            action = self.env.ref('virtual_fair.action_virtual_fair').\
                read()[0]
            form_view_name = 'virtual_fair.view_virtual_fair_form'
            action['views'] = [(self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = fair.id
            return action
        return
