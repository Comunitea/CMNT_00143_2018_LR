# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import pyodbc
from odoo import fields, models


class SqlServerConnector(object):

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

    def search_invoice(self, record):
        query = """SELECT COUNT(*)
                   FROM {} WHERE num_factura=? and serie_id=?;""".format(
                       self._table_name)
        self.cr.execute(query, (record.number, record.journal_id.sqlserver_id))
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
                    WHERE num_factura=? and serie_id=?;""".format(
                        self._table_name)
        self.cr.execute(
            query,
            (record.partner_id.cliente_id,
             record.partner_id.ref,
             record.journal_id.sqlserver_id,
             record.number,
             record.date_invoice,
             fields.Date.from_string(fields.Date.today()),
             pdf_file,
             record.number,
             record.journal_id.sqlserver_id,
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
             record.journal_id.sqlserver_id,
             record.number,
             fields.Date.from_string(record.date_invoice),
             fields.Date.from_string(fields.Date.today()),
             pdf_file))

    def upload_invoice(self, record, pdf_file):
        if self.search_invoice(record):
            self.refresh_invoice(record, pdf_file)
        else:
            self.create_invoice(record, pdf_file)

    def insert_payment(self, record):
        if record.get('fecha_recibo', False):

            query = """INSERT INTO {}(cliente_id,
                                      remesa_id,
                                      codigo_recibo_ag,
                                      factura,
                                      fecha_vto_ag,
                                      fecha_recibo,
                                      fecha_vto,
                                      importe,
                                      importe_ag)
                       VALUES(?,?,?,?,?,?,?,?,?);""".format(self._table_name)
            self.cr.execute(
                query,
                (record['cliente_id'],
                 record['remesa_id'],
                 record['codigo_recibo_ag'],
                 record['factura'],
                 record['fecha_vto_ag'],
                 record['fecha_recibo'],
                 record['fecha_vto'],
                 record['importe'],
                 record['importe_ag'],
                 ))
        else:
            query = """INSERT INTO {}(cliente_id,
                                      remesa_id,
                                      codigo_recibo_ag,
                                      factura,
                                      fecha_vto_ag,
                                      fecha_vto,
                                      importe,
                                      importe_ag)
                                   VALUES(?,?,?,?,?,?,?,?);""".format(
                self._table_name)
            self.cr.execute(
                query,
                (record['cliente_id'],
                 record['remesa_id'],
                 record['codigo_recibo_ag'],
                 record['factura'],
                 record['fecha_vto_ag'],
                 record['fecha_vto'],
                 record['importe'],
                 record['importe_ag'],
                 ))


class SqlserverConfiguration(models.Model):
    _name = 'sql.server.configuration'

    # Driver necesario:
    # https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows#using-an-odbc-driver
    SQLSERVER_DRIVERS = [
        ('{SQL Server}', '{SQL Server}'),
        ('{SQL Native Client}', '{SQL Native Client}'),
        ('{SQL Server Native Client 10.0}', '{SQL Server Native Client 10.0}'),
        ('{SQL Server Native Client 11.0}', '{SQL Server Native Client 11.0}'),
        ('{ODBC Driver 11 for SQL Server}', '{ODBC Driver 11 for SQL Server}'),
        ('{ODBC Driver 13 for SQL Server}', '{ODBC Driver 13 for SQL Server}'),
        ('{ODBC Driver 13.1 for SQL Server}',
         '{ODBC Driver 13.1 for SQL Server}'),
        ('{ODBC Driver 17 for SQL Server}', '{ODBC Driver 17 for SQL Server}')
    ]

    driver = fields.Selection(SQLSERVER_DRIVERS, required=True)
    server = fields.Char(required=True)
    database = fields.Char(required=True)
    user = fields.Char(required=True)
    password = fields.Char(required=True)
    table_name = fields.Char(required=True)
    model_type = fields.Selection(
        [('account.invoice', 'Invoices'),
         ('payment.order', 'Payments')], required=True)
    trusted = fields.Boolean()
    trusted_value = fields.Char(compute='_compute_trusted_value')

    def _compute_trusted_value(self):
        # Se debe de enviar valor yes/no
        for config in self:
            if config.trusted:
                config.trusted_value = 'yes'
            else:
                config.trusted_value = 'no'

    def upload_invoice(self, invoice, pdf_file):
        sql_connection = SqlServerConnector(
            self.driver,
            self.server,
            self.database,
            self.user,
            self.password,
            self.table_name,
            self.trusted_value)
        sql_connection.upload_invoice(invoice, pdf_file)
        sql_connection.close_cursor()

    def upload_payment(self, payment_order):
        sql_connection = SqlServerConnector(
            self.driver,
            self.server,
            self.database,
            self.user,
            self.password,
            self.table_name,
            self.trusted_value)
        for line in payment_order.bank_line_ids:
            if line.partner_id.cliente_id:
                for payment_line in line.payment_line_ids:
                    payment_order_values = {
                        'cliente_id': line.partner_id.cliente_id,
                        'remesa_id':
                        ''.join([x for x in line.order_id.name if x.isdigit()]),
                        'codigo_recibo_ag': line.name ,
                        'factura': payment_line.communication,
                        'fecha_vto_ag': fields.Date.from_string(line.date),
                        'fecha_vto':
                        fields.Date.from_string(payment_line.date),
                        'importe': payment_line.amount_company_currency,
                        'importe_ag': line.amount_currency,
                    }
                    if payment_line.move_line_id and \
                            payment_line.move_line_id.invoice_id:
                        payment_order_values.update(
                            {'fecha_recibo':
                                 payment_line.move_line_id.invoice_id.date_invoice})
                    sql_connection.insert_payment(payment_order_values)
        sql_connection.close_cursor()

    def delete_payment(self):
        sql_connection = SqlServerConnector(
            self.driver,
            self.server,
            self.database,
            self.user,
            self.password,
            self.table_name,
            self.trusted_value)
        # Si lo hacemos con un @job, cuando se ejecute, ya no existiren las lineas de pago bancario,
        # Se puede hacer un delete con where remesa_id = ''.join([x for x in line.order_id.name if x.isdigit()])
        # valdría así, si no, solo se me ocurre, o pasar los datos de las lineas a la función antes de hacer el el super() de la funcion cancel
        # o hacerlo sin el @job.
        #sql_connection.delete_payment(datos_necesarios_para_borrar)
        sql_connection.close_cursor()
