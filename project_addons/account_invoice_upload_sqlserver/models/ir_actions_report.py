# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import pyodbc
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.queue_job.job import job


class UploadInvoice(object):

    def __init__(self,
                 driver,
                 server,
                 database,
                 user,
                 password,
                 table_name,
                 trusted='no'):
        '''
            Starts a connection to sqlserver and get cursor
            :param driver: microsoft sql server driver
            https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows#using-an-odbc-driver
            :param server: database host
            :param database: Database
            :param user: User
            :param password: password
            :param Trusted: Trusted connection allowed parameters yes/no
        '''
        connection_string = 'DRIVER={};SERVER={};DATABASE={};UID={};PWD={};Trusted_Connection={}'
        self._connection_string = connection_string.format(
            driver, server, database, user, password, trusted)
        self._start_cursor()
        self._table_name = table_name

    def _start_cursor(self):
        self._connection = pyodbc.connect(self._connection_string)
        self.cr = None
        self.cr = self._connection.cursor()
        self._connection.autocommit = False

    def close_cursor(self):
        self.cr.commit()
        self._connection.autocommit = True
        self.cr.close()
        self._connection.close()

    def search_invoice(self, invoice_number):
        query = """SELECT COUNT(*)
                   FROM {} WHERE num_factura=?;""".format(self._table_name)
        self.cr.execute(query, invoice_number)
        result = self.cr.fetchone()
        if result and result[0] != 0:
            return True
        return False

    def refresh_invoice(self, record, pdf_file):
        query = """UPDATE {}
                    SET cliente_id=?,
                        cliente_codigo=?,
                        serie_id=?,
                        num_factura=?,
                        fecha_factura=?,
                        fecha_alta=?,
                        fichero=?
                    WHERE num_factura=? and cliente_id=?;""".format(
                        self._table_name)
        self.cr.execute(
            query,
            (record.partner_id.cliente_id,
             record.partner_id.ref,
             # Esto va a romper en cuanto un diario no tenga como
             # codigo corto S#
             record.journal_id.code[1],
             record.number,
             record.date_invoice,
             fields.Date.from_string(fields.Date.today()),
             pdf_file,
             record.number,
             record.partner_id.cliente_id,
             ))

    def create_invoice(self, record, pdf_file):
        query = """INSERT INTO {}(cliente_id,
                                  cliente_codigo,
                                  serie_id,
                                  num_factura,
                                  fecha_factura,
                                  fecha_alta,
                                  fichero)
                   VALUES(?,?,?,?,?,?,?);""".format(self._table_name)
        self.cr.execute(
            query,
            (record.partner_id.cliente_id,
             record.partner_id.ref,
             # Esto va a romper en cuanto un diario no tenga como codigo
             # corto S#
             record.journal_id.code[1],
             record.number,
             fields.Date.from_string(record.date_invoice),
             fields.Date.from_string(fields.Date.today()),
             pdf_file))

    def upload(self, record, pdf_file):
        if not record.partner_id.ref.isdigit():
            raise UserError(_('Partner reference not numeric'))
        if self.search_invoice(record.number):
            self.refresh_invoice(record, pdf_file)
        else:
            self.create_invoice(record, pdf_file)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @job
    def upload_invoice(self, record, attachment):
        pdf_file = base64.b64decode(attachment.datas)
        driver = self.env['ir.config_parameter'].get_param(
            'upload_invoice.driver')
        server = self.env['ir.config_parameter'].get_param(
            'upload_invoice.server')
        database = self.env['ir.config_parameter'].get_param(
            'upload_invoice.database')
        user = self.env['ir.config_parameter'].get_param(
            'upload_invoice.user')
        password = self.env['ir.config_parameter'].get_param(
            'upload_invoice.password')
        table_name = self.env['ir.config_parameter'].get_param(
            'upload_invoice.table_name')
        trusted = self.env['ir.config_parameter'].get_param(
            'upload_invoice.trusted')
        sql_connection = UploadInvoice(
            driver,
            server,
            database,
            user,
            password,
            table_name,
            trusted)
        sql_connection.upload(record, pdf_file)
        sql_connection.close_cursor()

    @api.multi
    def postprocess_pdf_report(self, record, buffer):
        res = super().postprocess_pdf_report(record, buffer)
        if record._name == 'account.invoice' and res:
            self.with_delay().upload_invoice(record, res)
        return res
