# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api


class log_import_spl(models.Model):

    _name = 'log.import.spl'

    name = fields.Char()
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    date = fields.Date('Date', 
                       required=True,
                       default=fields.Date.context_today,
                       readonly=True)
    supplier_pricelist_ids = fields.One2many(comodel_name='product.supplierinfo',
                                             inverse_name='log_id',
                                             string="Pricelist registers",
                                             readonly=True)
    
