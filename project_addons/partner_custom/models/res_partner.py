# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import uuid
import io

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
    urgent = fields.Boolean('Urgent', help='Default urgent for partner orders\nPlus 3.20%')
    id_prov = fields.Integer('Id Prov')

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

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        from_import = self._context.get('import_file', False)
        if vals.get('ref', False) and not from_import:
            self.env['ir.model.data'].sudo().create({
                    'name': vals['ref'],
                    'model': 'res.partner',
                    'module': '',
                    'res_id': res.id,
                    'noupdate': False
                })
        return res

    @api.multi
    def _export_rows(self, fields, batch_invalidate=True):
        """ Export fields of the records in ``self``.

            :param fields: list of lists of fields to traverse
            :param batch_invalidate:
                whether to clear the cache for the top-level object every so often (avoids huge memory consumption when exporting large numbers of records)
            :return: list of lists of corresponding values
        """
        import_compatible = self.env.context.get('import_compat', True)
        lines = []

        def splittor(rs):
            """ Splits the self recordset in batches of 1000 (to avoid
            entire-recordset-prefetch-effects) & removes the previous batch
            from the cache after it's been iterated in full
            """
            for idx in range(0, len(rs), 1000):
                sub = rs[idx:idx+1000]
                for rec in sub:
                    yield rec
                rs.invalidate_cache(ids=sub.ids)
        if not batch_invalidate:
            splittor = lambda rs: rs

        # both _ensure_xml_id and the splitter want to work on recordsets but
        # neither returns one, so can't really be composed...
        xids = dict(self.__ensure_xml_id(skip=['id'] not in fields))
        # memory stable but ends up prefetching 275 fields (???)
        for record in splittor(self):
            # main line of record, initially empty
            current = [''] * len(fields)
            lines.append(current)

            # list of primary fields followed by secondary field(s)
            primary_done = []

            # process column by column
            for i, path in enumerate(fields):
                if not path:
                    continue

                name = path[0]
                if name in primary_done:
                    continue

                if name == '.id':
                    current[i] = str(record.id)
                elif name == 'id':
                    xid = xids.get(record)
                    assert xid, "no xid was generated for the record %s" % record
                    current[i] = xid
                else:
                    field = record._fields[name]
                    value = record[name]

                    # this part could be simpler, but it has to be done this way
                    # in order to reproduce the former behavior
                    if not isinstance(value, models.BaseModel):
                        current[i] = field.convert_to_export(value, record)
                    else:
                        primary_done.append(name)

                        # in import_compat mode, m2m should always be exported as
                        # a comma-separated list of xids in a single cell
                        if import_compatible and field.type == 'many2many' and len(path) > 1 and path[1] == 'id':
                            xml_ids = [xid for _, xid in value.__ensure_xml_id()]
                            current[i] = ','.join(xml_ids) or False
                            continue

                        # recursively export the fields that follow name; use
                        # 'display_name' where no subfield is exported
                        fields2 = [(p[1:] or ['display_name'] if p and p[0] == name else [])
                                   for p in fields]
                        lines2 = value._export_rows(fields2, batch_invalidate=False)
                        if lines2:
                            # merge first line with record's main line
                            for j, val in enumerate(lines2[0]):
                                if val or isinstance(val, bool):
                                    current[j] = val
                            # append the other lines at the end
                            lines += lines2[1:]
                        else:
                            current[i] = False

        return lines




    def __ensure_xml_id(self, skip=False):
        """ Create missing external ids for records in ``self``, and return an
                    iterator of pairs ``(record, xmlid)`` for the records in ``self``.

                :rtype: Iterable[Model, str | None]
                """
        if skip:
            return ((record, None) for record in self)

        if not self:
            return iter([])

        if not self._is_an_ordinary_table():
            raise Exception(
                "You can not export the column ID of model %s, because the "
                "table %s is not an ordinary table."
                % (self._name, self._table))

        modname = ''

        cr = self.env.cr
        cr.execute("""
                    SELECT res_id, module, name
                    FROM ir_model_data
                    WHERE model = %s AND res_id in %s
                """, (self._name, tuple(self.ids)))
        xids = {
            res_id: (module, name)
            for res_id, module, name in cr.fetchall()
        }

        def to_xid(record_id):
            (module, name) = xids[record_id]
            return ('%s.%s' % (module, name)) if module else name

        # create missing xml ids
        missing = self.filtered(lambda r: r.id not in xids)
        if not missing:
            return (
                (record, to_xid(record.id))
                for record in self
            )
        for r in missing:
            if r.ref:
                name = r.ref
            else:
                name = '%s_%s_%s' % (
                    r._table,
                    r.id,
                    uuid.uuid4().hex[:8],
                )
            xids.update(
                {r.id: (modname, name)})

        fields = ['module', 'model', 'name', 'res_id']
        cr.copy_from(io.StringIO(
            u'\n'.join(
                u"%s\t%s\t%s\t%d" % (
                    modname,
                    record._name,
                    xids[record.id][1],
                    record.id,
                )
                for record in missing
            )),
            table='ir_model_data',
            columns=fields,
        )
        self.env['ir.model.data'].invalidate_cache(fnames=fields)

        return (
            (record, to_xid(record.id))
            for record in self
        )


    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'associate' in vals:
            self.check_associate(vals['associate'])

    @api.multi
    def check_associate(self, active=False):
        for partner in self:
            res = partner.get_associate_contract(active)
            if res:
                partner.message_post("Se ha creado un nuevo contrato")


    @api.model
    def get_associate_contract(self, active, create_if_active=False):

        company_id = self.company_id or self.env.user.company_id
        new_tag = self.env.ref('partner_custom.analytic_tag_name_associate_quote')
        contract_domain = [('name', '=', new_tag.name), ('company_id', '=', company_id.id),
                           ('contract_type', '=', 'sale')]
        contract_template_id = self.env['account.analytic.contract'].search(contract_domain, limit=1)
        if not contract_template_id:
            raise ValidationError(_("No contract template for {}".format(new_tag.name)))

        domain = [('partner_id', '=', self.id),
                  ('recurring_invoices', '=', True),
                  ('contract_template_id', '=', contract_template_id.id)]
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
                        'recurring_next_date': start_date + analytic_id.get_relative_delta(contract_template_id.recurring_rule_type, contract_template_id.recurring_interval)}
                analytic_id.write(vals)
                return analytic_id


        # CREO UNO NUEVO
        vals = {
            'name': '{}'.format('Cuota socio'),
            'partner_id': self.id,
            'company_id': company_id.id,
            'recurring_invoices': True,
            'contract_template_id': contract_template_id.id,
            'tag_ids': [(6,0, [new_tag.id])]
        }
        account_id = analytic_obj.new(vals)
        account_id._onchange_contract_template_id()
        values = analytic_obj._convert_to_write(account_id._cache)
        recurring_next_date = start_date + account_id.get_relative_delta(contract_template_id.recurring_rule_type, contract_template_id.recurring_interval)
        values.update(date_start=start_date, recurring_next_date=recurring_next_date)
        analytic_id = analytic_obj.create(values)
        return analytic_id

