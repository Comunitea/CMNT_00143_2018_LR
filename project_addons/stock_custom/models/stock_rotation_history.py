# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, _

MONTHS = {
    '1': 'January',
}


class StockRotationHistory(models.Model):

    _name = 'stock.rotation.history'

    _sql_constraints = [
        ('product_unique', 'unique (product_id)', 'Product must be unique')
    ]

    product_id = fields.Many2one('product.product', 'Product')
    date = fields.Date('Date importation', default=fields.Date.today())
    month_1 = fields.Float('01 Month Ago')
    month_2 = fields.Float('02 Month Ago')
    month_3 = fields.Float('03 Month Ago')
    month_4 = fields.Float('04 Month Ago')
    month_5 = fields.Float('05 Month Ago')
    month_6 = fields.Float('06 Month Ago')
    month_7 = fields.Float('07 Month Ago')
    month_8 = fields.Float('08 Month Ago')
    month_9 = fields.Float('09 Month Ago')
    month_10 = fields.Float('10 Month Ago')
    month_11 = fields.Float('11 Month Ago')
    month_12 = fields.Float('12 Month Ago')
