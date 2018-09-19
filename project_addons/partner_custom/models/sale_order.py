# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    associate = fields.Boolean(related="partner_id.associate")
    financiable_payment = fields.Boolean('Financiable', help="Default financiable for partner orders")
    cash_payment = fields.Boolean('Pago contado', help="Default payment for partner orders")
    urgent = fields.Boolean("Urgent", help='Plus 3,20%')
    direct = fields.Boolean('Direct', help='If checked, Serie 2')

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        return invoice_vals

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            values = {
                'financiable_payment': self.partner_id.financiable_payment,
                'cash_payment': self.partner_id.cash_payment,
                'urgent': self.partner_id.urgent,
                'direct': self.partner_id.direct,
            }
        else:
            values = {
                'financiable_payment': False,
                'cash_payment': False,
                'urgent': False,
                'direct': False,
            }
        self.update(values)
