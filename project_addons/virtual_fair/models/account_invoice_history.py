# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re
from odoo import api, fields, models


class AccountInvoiceHistory(models.Model):
    _name = 'account.invoice.history'

    fchaFra = fields.Date()
    numFra = fields.Char()
    codPr = fields.Char()
    nomProv = fields.Char()
    codS = fields.Char()
    nombSocio = fields.Char()
    numFraSc = fields.Char()
    fchaFraSc = fields.Date()
    base1 = fields.Float()
    base2 = fields.Float()
    iva1 = fields.Float()
    iva2 = fields.Float()
    pp = fields.Float()
    etiqueta = fields.Char()

    associate_id = fields.Many2one(
        'res.partner', compute='_compute_associate_id', store=True)
    supplier_id = fields.Many2one(
        'res.partner', compute='_compute_supplier_id', store=True)
    clean_reference = fields.Char(
        compute='_compute_clean_reference', store=True)

    @api.depends('numFra')
    def _compute_clean_reference(self):
        for inv_hist in self:
            if not inv_hist.numFra:
                continue
            inv_hist.clean_reference = inv_hist.numFra and \
                re.sub('[^A-Za-z0-9]+', '', inv_hist.numFra) or ''

    @api.depends('codS')
    def _compute_associate_id(self):
        for inv_hist in self:
            if not inv_hist.codS:
                continue
            partner = self.env['res.partner'].search(
                [('ref', '=', inv_hist.codS)])
            if partner:
                inv_hist.associate_id = partner[0].id

    @api.depends('codPr')
    def _compute_supplier_id(self):
        for inv_hist in self:
            if not inv_hist.codPr:
                continue
            supplier = self.env['res.partner'].search(
                [('ref', '=', inv_hist.codPr)])
            if supplier:
                inv_hist.supplier_id = supplier[0].id
