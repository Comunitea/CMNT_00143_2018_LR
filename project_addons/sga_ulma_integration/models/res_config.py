# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, api, _
from odoo.addons.stock_move_selection_wzd.models.stock_picking_type import SGA_STATES
from odoo.exceptions import Warning, UserError

ULMA_PARAMS = ['ulma_user', 'ulma_pass', 'ulma_host', 'ulma_port', 'ulma_sid',  'ulma_database', 'mmmout_table', 'mmminp_table', \
'packing_table', 'fdw', 'oracle_extension', 'oracle_server', 'oracle_mmmout', 'oracle_mmminp', 'oracle_packing', 'ulma_cajas', 'ulma_cajas']


class ConfigUlmaData(models.TransientModel):

    _inherit = 'res.config.settings'

    ulma_user = fields.Char('ULMA db user', help="User name needed to connect to the ULMA db")
    ulma_pass = fields.Char('ULMA db password', help="Password needed to connect to the ULMA db")
    ulma_host = fields.Char('ULMA db host', help="Host needed to connect to the ULMA db")
    ulma_port = fields.Char('ULMA db port', help="Port needed to connect to the ULMA db")
    ulma_sid = fields.Char('ULMA db SID', help="SID/database needed to connect to the ULMA db")
    ulma_database = fields.Char('ULMA server name', help="Server name, needed for connection.")
    oracle_extension = fields.Boolean('Oracle Ext.')
    oracle_server = fields.Boolean('Server Link')
    oracle_mmmout = fields.Boolean('MMMOUT table linked')
    oracle_mmminp = fields.Boolean('MMMINP table linked')
    oracle_packing = fields.Boolean('packing table linked')
    oracle_cajas = fields.Boolean('cajas table linked')
    mmmout_table = fields.Char('MMMOUT table', help='Name of the mmmout table')
    mmminp_table = fields.Char('MMMINP table', help='Name of the mmminp table')
    packing_table = fields.Char('Packinglist table', help='Name of the packinglist table')
    ulma_cajas = fields.Char('Cajas table', help='Ulma cajas table')
    fdw = fields.Selection([('oracle_fdw', 'Oracle'), ('postgres_fdw', 'Postgres')], default="oracle_fdw", string='FDW', help='Foreign Data Wrapper')


    @api.model
    def get_values(self):
        ICP =self.env['ir.config_parameter'].sudo()
        res = super(ConfigUlmaData, self).get_values()
        for param in ULMA_PARAMS:
            value= ICP.get_param('sga_ulma_integration.{}'.format(param), False)
            res.update({param: value})
        return res

    @api.multi
    def set_values(self):
        super(ConfigUlmaData, self).set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        for param in ULMA_PARAMS:
            ICP.set_param('sga_ulma_integration.{}'.format(param), self[param])


    def check_extension(self):

        set_param = self.env['ir.config_parameter'].sudo().set_param
        self.env.cr.execute("""select * from pg_extension where extname = '%s'""" % (self.fdw))

        if self.env.cr.rowcount:
            self.oracle_extension = True
        else:
            self.oracle_extension = False



        self.env.cr.execute("""select * from pg_foreign_server where srvname = '%s'""" % (self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_server = True
        else:
            self.oracle_server = False
        self.env.cr.execute(
            """select * from information_schema.foreign_tables where foreign_table_name = 'ulma_mmmout' and foreign_server_name = '%s'""" % (
                self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_mmmout = True
        else:
            self.oracle_mmmout = False
        self.env.cr.execute(
            """select * from information_schema.foreign_tables where foreign_table_name = 'ulma_mmminp' and foreign_server_name = '%s'""" % (
                self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_mmminp = True
        else:
            self.oracle_mmminp = False
        self.env.cr.execute(
            """select * from information_schema.foreign_tables where foreign_table_name = 'ulma_packinglist' and foreign_server_name = '%s'""" % (
                self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_packing = True
        else:
            self.oracle_packing = False

        self.env.cr.execute(
            """select * from information_schema.foreign_tables where foreign_table_name = 'ulma_cajas' and foreign_server_name = '%s'""" % (
                self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_cajas = True
        else:
            self.oracle_cajas = False
        return

    def check_server_link(self):
        self.env.cr.execute("""select * from pg_foreign_server where srvname = '%s'""" % (self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_server = True
        else:
            self.oracle_server = False
    
    def check_tables(self):
        self.env.cr.execute("""select * from information_schema.foreign_tables where foreign_table_name = 'ulma_mmmout' and foreign_server_name = '%s'""" % (self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_mmmout = True
        else:
            self.oracle_mmmout = False

        self.env.cr.execute("""select * from information_schema.foreign_tables where foreign_table_name = 'ulma_mmminp' and foreign_server_name = '%s'""" % (self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_mmminp = True
        else:
            self.oracle_mmminp = False

        self.env.cr.execute("""select * from information_schema.foreign_tables where foreign_table_name = 'ulma_packinglist' and foreign_server_name = '%s'""" % (self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_packing = True
        else:
            self.oracle_packing = False

        self.env.cr.execute("""select * from information_schema.foreign_tables where foreign_table_name = 'ulma_cajas' and foreign_server_name = '%s'""" % (self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_packing = True
        else:
            self.oracle_packing = False
    
    def init_extension(self):
        ## Create extension
        self.env.cr.execute("""CREATE EXTENSION IF NOT EXISTS %s WITH SCHEMA public""" % (self.fdw))        

        ## Comment on extension
        self.env.cr.execute("""COMMENT ON EXTENSION %s IS 'foreign data wrapper'""" % (self.fdw))

    
    def link_to_server(self):
        ## Create remote server
        if self.fdw == 'oracle_fdw':
            self.env.cr.execute("""CREATE SERVER %s FOREIGN DATA WRAPPER %s OPTIONS (dbserver '%s:%s/%s')""" % (self.ulma_database, self.fdw, self.ulma_host, self.ulma_port, self.ulma_sid))
        else:
            self.env.cr.execute("""CREATE SERVER %s FOREIGN DATA WRAPPER %s OPTIONS (host '%s', dbname '%s')""" % (self.ulma_database, self.fdw, self.ulma_host, self.ulma_sid))

        ## Create user mapping
        self.env.cr.execute("""CREATE USER MAPPING FOR odoo server %s OPTIONS (password '%s', user '%s')""" % (self.ulma_database, self.ulma_pass, self.ulma_user))

        ## Grant privileges on foreign data to odoo user
        self.env.cr.execute("""GRANT ALL PRIVILEGES ON FOREIGN DATA WRAPPER %s TO odoo""" % (self.fdw))

        ## Grant usage on foreign server to odoo user
        self.env.cr.execute("""GRANT USAGE ON FOREIGN SERVER %s TO odoo""" % (self.ulma_database))
    
    def create_tables(self):
        self.create_table_mmmout()
        self.create_table_mmminp()
        self.create_table_packing()
        self.create_table_cajas()

    
    def create_table_mmmout(self):

        if self.fdw == 'oracle_fdw':
            table_mod = 'TABLE'
            primary_mod = 'SERIAL'
        else:
            table_mod = 'table_name'
            primary_mod = 'integer NOT NULL'

        ## Create foreign table mmmout
        self.env.cr.execute("""CREATE FOREIGN TABLE ulma_mmmout (mmmabclog character varying(1), mmmacccolcod numeric(9,0), mmmacp character(1), 
        mmmalgent character varying(1), mmmalgsal character varying(1), mmmambreg character varying(1), mmmartdes character varying(40), 
        mmmartref character varying(16), mmmcanuni numeric(9,0), mmmcmdref character varying(9) NOT NULL, mmmcntdorref character varying(18), 
        id %s, mmmcrirot character varying(20),  mmmdesdes character varying(70), mmmdesdir1 character varying(70), 
        mmmdesdir2 character varying(70), mmmdesdir3 character varying(70), mmmdesdir4 character varying(70), mmmdim character varying(4), 
        mmmdisref character varying(9), mmmentdes character varying(70), mmmentdir1 character varying(70), mmmentdir2 character varying(70), 
        mmmentdir3 character varying(70), mmmentdir4 character varying(70), mmmexpordref character varying(15), mmmges character varying(9) NOT NULL, 
        mmmlot character varying(20), mmmmaxudsdim numeric(9,0), mmmmaxudsdis numeric(9,0), mmmminudsdis numeric(9,0), mmmpicent character varying(1), 
        mmmpicsal character varying(1), mmmremdes character varying(70), mmmremdir1 character varying(70), mmmremdir2 character varying(70), 
        mmmremdir3 character varying(70), mmmremdir4 character varying(70), mmmres character varying(9), mmmresmsj character varying(80), mmmsecada numeric(9,0), 
        mmmsecdis numeric(9,0), mmmsesid numeric(9,0), mmmterproref character varying(16), mmmubidesref character varying(16), mmmubioriref character varying(16), 
        mmmzondesref character varying(4), momcre timestamp, momlec timestamp, mmmartean character varying(30), mmmexpordfusref character varying(15), 
        mmmnecman character varying(4), mmmobs character varying(255), mmmpesfin numeric(9,3), mmmsorrut character varying(30), mmmtolpes numeric(2,0), 
        mmmubichkref character varying(16), mmmacccod numeric(9,0), mmmacpmot character varying(4), mmmartapi character varying(1), mmmbatch character varying(9), 
        mmmdorhue character varying(1), mmmfeccad timestamp, mmmgraocu numeric(3,0), mmmmomexp timestamp, mmmmonlot character varying(1), mmmrecmaqref character(10), 
        mmmrecref character varying(15), mmmterref character varying(16), mmmtrades character varying(70), mmmtraref character varying(16), 
        mmmurgnte character varying(1)) SERVER %s OPTIONS (%s '%s')""" % (primary_mod, self.ulma_database, table_mod, self.mmmout_table))
    
    def create_table_mmminp(self):

        if self.fdw == 'oracle_fdw':
            table_mod = 'TABLE'
            primary_mod = 'SERIAL'
        else:
            table_mod = 'table_name'
            primary_mod = 'integer NOT NULL'

        ## Create foreign table mmminp
        self.env.cr.execute("""CREATE FOREIGN TABLE ulma_mmminp (mmmacp character varying(1), mmmartref character varying(16), mmmcanuni numeric(9,0), 
        mmmcmdref character varying(9) NOT NULL, mmmcntdorref character varying(18), id %s, mmmcrirot character varying(20), 
        mmmdisref character varying(9), mmmexpordref character varying(15), mmmges character varying(9) NOT NULL, mmmlot character varying(20), 
        mmmres character varying(9), mmmresmsj character varying(80), mmmsecada numeric(9,0), mmmsecdis numeric(9,0), mmmsesid numeric(9,0), 
        mmmubidesref character varying(16), mmmubiorief character varying(16), momcre timestamp, momlec timestamp, mmmacccolcod numeric(9,0), mmmobs character varying(255), 
        mmmexpordfusref character varying(15), mmmpesfin numeric(9,3), mmmacccod numeric(9,0), mmmrecmaqref character(10), mmmacpmot character varying(4), 
        mmmcntdordes character varying(18), mmmcntdordori character varying(18), mmmrecref character varying(15)) 
        SERVER %s OPTIONS (%s '%s')""" % (primary_mod, self.ulma_database, table_mod, self.mmminp_table))

    
    def create_table_packing(self):

        if self.fdw == 'oracle_fdw':
            table_mod = 'TABLE'
            primary_mod = 'SERIAL'
        else:
            table_mod = 'table_name'
            primary_mod = 'integer NOT NULL'

        ## Create foreign table packinglist
        self.env.cr.execute("""CREATE FOREIGN TABLE ulma_packinglist (mmmexpordref character varying(15), estado character varying(1), mmmsesid numeric(9,0), 
        mmmbatch numeric(9,0), status character varying(1), id %s, mmmres character varying(9), mmmcmdref character varying(9)) 
        SERVER %s OPTIONS (%s '%s')""" % (primary_mod, self.ulma_database, table_mod, self.packing_table))

        #ADD Key to enable table editing
        self.env.cr.execute("""ALTER FOREIGN TABLE ulma_packinglist ALTER "id" OPTIONS (ADD key 'true');""")

    def create_table_cajas(self):

        if self.fdw == 'oracle_fdw':
            table_mod = 'TABLE'
            primary_mod = 'SERIAL'
        else:
            table_mod = 'table_name'
            primary_mod = 'integer NOT NULL'

        ## Create foreign table cajas
        self.env.cr.execute("""CREATE FOREIGN TABLE ulma_cajas (matricula character varying(15), referencia character varying(20), hueco numeric(9,0), 
        cantidad numeric(9,0), tipo character varying(15), caja_id numeric(15), procesado character varying(1), id %s,
        origen character varying(9), confirmado character varying(1), fecha timestamp) 
        SERVER %s OPTIONS (%s '%s')""" % (primary_mod, self.ulma_database, table_mod, self.ulma_cajas))

        #ADD Key to enable table editing
        self.env.cr.execute("""ALTER FOREIGN TABLE ulma_cajas ALTER "id" OPTIONS (ADD key 'true');""")


    def drop_tables(self):
        ## Deletes the tables
        self.drop_mmmout()
        self.drop_mmminp()
        self.drop_packinglist()
        self.drop_cajas()

    def drop_mmmout(self):
        ## Deletes the mmmout table
        self.env.cr.execute("""DROP FOREIGN TABLE ulma_mmmout""")
    
    def drop_mmminp(self):
        ## Deletes the mmminp table
        self.env.cr.execute("""DROP FOREIGN TABLE ulma_mmminp""")
    
    def drop_packinglist(self):
        ## Deletes the packinglist table
        self.env.cr.execute("""DROP FOREIGN TABLE ulma_packinglist""")

    def drop_cajas(self):
        ## Deletes the cajas table
        self.env.cr.execute("""DROP FOREIGN TABLE ulma_cajas""")

    @api.model
    def sync_folders(self):
        super(ConfigUlmaData, self).sync_folders()
        self.env['stock.batch.picking'].get_from_ulma()
        self.env['ulma.cajas'].check_packages_from_adaia()
