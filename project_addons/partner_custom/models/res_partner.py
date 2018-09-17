# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ResPartner(models.Model):

    _inherit = 'res.partner'

    associate = fields.Boolean('Associate')
    financiable_payment = fields.Boolean('Financiable', help="Default financiable for partner orders\n60 days due date >> Minus 1% in discount")
    cash_payment = fields.Boolean('Pash payment', help="Default payment for partner orders")
    direct = fields.Boolean('Direct', help='If checked, Serie 2')
    urgent = fields.Boolean('Urgent', help = 'Default urgent for partner orders\nPlus 3.20%')

    @api.onchange('associate')
    def _onchange_associate(self):
        ICP = self.env['ir.config_parameter']
        for partner in self:
            if not partner.associate:
                partner.financiable_payment = False
                partner.urgent = False
                partner.direct = False

                ##Todo pendiente de sale comission// Reseteo pendiente del vendedor  EMPRESA
                self.user_id =  False
                field_pricelist = 'default_no_associate_sale_pricelist'
            else:
                field_pricelist = 'default_associate_sale_pricelist'

            partner.property_product_pricelist = self.env['product.pricelist'].browse(int(ICP.get_param(field_pricelist)))
