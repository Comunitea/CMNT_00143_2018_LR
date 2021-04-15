# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api


class SupplierDiscountGroup(models.Model):

    _name = 'supplier.discount.group'

    name = fields.Char()
    desciption = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Supplier')
    discount = fields.Char('Discount (%)')

    _sql_constraints = [
        ('name_partner_unique', 'unique(name, partner_id)', 'Discount group names must be unique !'),
    ]


    @api.model
    def validate_chained_discount(self, discount_str):
        try:
            splited_discount = discount_str.split('+')
            for val in splited_discount:
                float(val)
        except:
            return False
        return True

    @api.onchange('discount')
    def onchange_discount(self):
        if not self.discount:
            self.discount = '0.00'
        valid = self.validate_chained_discount(self.chained_discount)
        if not valid:
            msg = _("Format must be something like 10.5 or 10.5+2+3.4 etc \
                    No strings or ',' allowwed")
            self.discount = '0.00'
            return {'warning': {'title': 'Warning',
                                'message': msg}}