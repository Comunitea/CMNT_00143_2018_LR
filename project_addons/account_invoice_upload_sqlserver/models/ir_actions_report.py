# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo.addons.queue_job.job import job


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @job
    def upload_invoice(self, record, attachment):
        if record.partner_id.cliente_id:  # Solo se envia si tenemos
            # establecido el campo de identiifcaiónd e cliente en web
            if not record.partner_id.ref.isdigit():
                raise ValidationError(_('Partner reference not numeric'))
            if not record.journal_id.sqlserver_id:
                raise ValidationError(
                    _('Journal {} without sqlserver id').format(
                        record.journal_id.name))

            sql_server_config = self.env['sql.server.configuration'].search([
                ('model_type', '=', 'account.invoice')
            ])
            if not sql_server_config:
                raise ValidationError(_('Sql server configuration not found'))
            pdf_file = base64.b64decode(attachment.datas)
            sql_server_config.upload_invoice(record, pdf_file)

    @api.multi
    def postprocess_pdf_report(self, record, buffer):
        res = super().postprocess_pdf_report(record, buffer)
        if record._name == 'account.invoice' and \
                record.type in ('out_invoice', 'out_refund') and res:
            self.with_delay().upload_invoice(record, res)
        return res
