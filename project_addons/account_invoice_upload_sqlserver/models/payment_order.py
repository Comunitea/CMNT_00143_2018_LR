# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.queue_job.job import job


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    name = fields.Char(string='Name')

    def action_send_web(self):
        if self.payment_type == 'inbound':
            self.with_delay().upload_payment()

    @job
    def upload_payment(self):
        sql_server_config = self.env['sql.server.configuration'].search([
            ('model_type', '=', 'payment.order')
        ])
        if not sql_server_config:
            raise ValidationError(_('Sql server configuration not found'))
        sql_server_config.upload_payment(self)

    @job
    def delete_sqlserver_payment(self):
        sql_server_config = self.env['sql.server.configuration'].search([
            ('model_type', '=', 'payment.order')
        ])
        if not sql_server_config:
            raise ValidationError(_('Sql server configuration not found'))
        sql_server_config.delete_payment()

    def generate_move(self):
        res = super().generate_move()
        if self.payment_type == 'inbound':
            self.with_delay().upload_payment()
        return res

    def action_done_cancel(self):
        if self.payment_type == 'inbound':
            # Aquí, o pasamos todos los datos de las lineas a delete_sqlserver_payment
            # o para cuando se ejecute el job ya no existirán.
            # Ver comentario sqlserver_config.py linea 213.
            self.with_delay().delete_sqlserver_payment()
        return super().action_done_cancel()

