# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoiceHistory(models.Model):
    _name = 'account.invoice.history'

    #campos importados directamente de csv
    fechaFraProv = fields.Date()
    numFra = fields.Char()
    tipoProv = fields.Boolean()
    fcchaContPraProv = fields.Date()
    contab = fields.Boolean()
    codProv = fields.Char()
    nomProv = fields.Char()
    codSocio = fields.Char()
    nombSocio = fields.Char()
    fchaFraEm = fields.Date()
    numFraEm = fields.Char()
    base1 = fields.Float()
    base2 = fields.Float()
    iva1 = fields.Float()
    iva2 = fields.Float()
    pp = fields.Float()
    col = fields.Float()
    iva = fields.Boolean()
    etiqueta = fields.Char()
    nifProv = fields.Char()
    idPlazoPagoProv = fields.Char()
    linDirId = fields.Char()
    idProveedor = fields.Char()

    associated_id = fields.Many2one(compute='_compute_associated_id', store=True)
    supplier_id = fields.Many2one(compute='_compute_supplier_id', store=True)
    clean_ref = fields.Char(compute='_compute_clean_ref', store=True)

    @api.depends('numFra')
    def _compute_clean_reference(self):
        for inv_hist in self:
            if not inv_hist.numFra:
                continue
            inv_hist.clean_reference = inv_hist.numFra and \
                re.sub('[^A-Za-z0-9]+', '', inv_hist.numFra) or ''

    @api.depends('codSocio')
    def _compute_associated_id(self):
        for inv_hist in self:
            if not inv_hist.codSocio:
                continue
            partner = self.env['res.partner'].search(
                [('ref', '=', inv_hist.codSocio)])
            if partner:
                inv_hist.associated_id = partner[0].id

    @api.depends('codProv')
    def _compute_supplier_id(self):
        for inv_hist in self:
            if not inv_hist.codProv:
                continue
            supplier = self.env['res.partner'].search(
                [('ref', '=', inv_hist.codProv)])
            if supplier:
                inv_hist.supplier_id = supplier[0].id

