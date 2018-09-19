# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from datetime import date
#from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class ResPartner(models.Model):

    _inherit = 'res.partner'

    associate = fields.Boolean('Associate')
    financiable_payment = fields.Boolean('Financiable', help="Default financiable for partner orders\n60 days due date >> Minus 1% in discount")
    cash_payment = fields.Boolean('Cash payment', help="Default payment for partner orders")
    direct = fields.Boolean('Direct', help='If checked, Serie 2')
    urgent = fields.Boolean('Urgent', help = 'Default urgent for partner orders\nPlus 3.20%')

    @api.onchange('associate')
    def _onchange_associate(self):

        ICP = self.env['ir.config_parameter']
        print (self._context)
        partner = self
        if not partner.associate:
            partner.financiable_payment = False
            partner.urgent = False
            partner.direct = False

            ##Todo pendiente de sale comission// Reseteo pendiente del vendedor  EMPRESA
            partner.user_id =  False
            field_pricelist = 'default_no_associate_sale_pricelist'
        else:
            field_pricelist = 'default_associate_sale_pricelist'

        partner.property_product_pricelist = self.env['product.pricelist'].browse(int(ICP.get_param(field_pricelist)))



    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'associate' in vals:
            self.check_associate(vals['associate'])

    @api.multi
    def check_associate(self, active=False):
        for partner in self:
            res = partner.get_associate_account(active)
            if res:
                partner.message_post("Se ha creado un nuevo contrato")


    @api.model
    def get_associate_account(self, active, create_if_active=False):

        company_id = self.company_id or self.env.user.company_id
        new_tag = self.env.ref('partner_custom.analytic_tag_name_associate_quote')
        contract_domain = [('name', '=', new_tag.name), ('company_id', '=', company_id.id),
                           ('contract_type', '=', 'sale')]
        contract = self.env['account.analytic.contract'].search(contract_domain, limit=1)


        domain = [('partner_id', '=', self.id),
                  ('recurring_invoices', '=', True),
                  ('contract_template_id', '=', contract.id)]
        analytic_obj = self.env['account.analytic.account']
        #Desactivamos los contratos si deja de ser asociado
        if not active:
            analytic_id = analytic_obj.search(domain, limit=1)
            if analytic_id:
                analytic_id.active = False
            return False
        # Si se activa, miro si hay un contrato desactivado y lo activo estableciendo fecha de factura
        # VERIFICAR ESTE PUNTO
        start_date = fields.Date.from_string(fields.Date.context_today(self))
        if active and not create_if_active:
            domain = domain + [('active','=', False)]
            analytic_id = analytic_obj.search(domain, limit=1)
            if analytic_id:
                vals = {'active': True,
                        'recurring_next_date': start_date + analytic_id.get_relative_delta(contract.recurring_rule_type, contract.recurring_interval)}
                analytic_id.write(vals)
                return analytic_id


        # CREO UNO NUEVO
        vals = {
            'name': '{}'.format('Cuota socio'),
            'partner_id': self.id,
            'company_id': company_id.id,
            'recurring_invoices': True,
            'contract_template_id': contract.id,
            'tag_ids': [(6,0, [new_tag.id])]
        }
        account_id = analytic_obj.new(vals)
        account_id._onchange_contract_template_id()
        values = analytic_obj._convert_to_write(account_id._cache)
        recurring_next_date = start_date + account_id.get_relative_delta(contract.recurring_rule_type, contract.recurring_interval)
        values.update(date_start=start_date, recurring_next_date=recurring_next_date)
        analytic_id = analytic_obj.create(values)
        return analytic_id

