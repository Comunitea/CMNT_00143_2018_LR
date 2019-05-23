# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError

class ConfigUlmaData(models.TransientModel):

    _inherit = 'res.config.settings'

    ulma_user = fields.Char('ULMA db user', help="User name needed to connect to the ULMA db", required=True)
    ulma_pass = fields.Char('ULMA db password', help="Password needed to connect to the ULMA db", required=True)
    ulma_host = fields.Char('ULMA db host', help="Host needed to connect to the ULMA db", required=True)
    ulma_port = fields.Char('ULMA db port', help="Port needed to connect to the ULMA db", required=True)
    ulma_sid = fields.Char('ULMA db SID', help="SID/database needed to connect to the ULMA db", required=True)
    ulma_database = fields.Char('ULMA server name', help="Server name, needed for connection.", required=True)
    oracle_extension = fields.Boolean('Oracle Ext.', compute="check_extension", store=False)
    oracle_server = fields.Boolean('Server Link', compute="check_server_link", store=False)
    oracle_mmmout = fields.Boolean('MMMOUT table linked', compute="check_tables", store=False)
    oracle_mmminp = fields.Boolean('MMMINP table linked', compute="check_tables", store=False)
    mmmout_table = fields.Char('MMMOUT table', help='Name of the mmmout table', required=True)
    mmminp_table = fields.Char('MMMINP table', help='Name of the mmminp table', required=True)
    fdw = fields.Selection([('oracle_fdw', 'Oracle'), ('postgres_fdw', 'Postgres')], default="oracle_fdw", string='FDW', help='Foreign Data Wrapper', required=True)
    
    @api.model
    def get_values(self):
        ICP =self.env['ir.config_parameter']
        res = super(ConfigUlmaData, self).get_values()
        uu = ICP.get_param('ulma_user', False)
        up = ICP.get_param('ulma_pass', False)
        uh = ICP.get_param('ulma_host', False)
        upo = ICP.get_param('ulma_port', False)
        sid = ICP.get_param('ulma_sid', False)
        udb = ICP.get_param('ulma_database', False)
        out = ICP.get_param('mmmout_table', False)
        inp = ICP.get_param('mmminp_table', False)
        fdw = ICP.get_param('fdw', False)
        res.update(ulma_user=uu)
        res.update(ulma_pass=up)
        res.update(ulma_host=uh)
        res.update(ulma_port=upo)
        res.update(ulma_sid=sid)
        res.update(ulma_database=udb)
        res.update(mmmout_table=out)
        res.update(mmminp_table=inp)
        res.update(fdw=fdw)
        return res

    @api.multi
    def set_values(self):
        super(ConfigUlmaData, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('ulma_user', self.ulma_user)
        set_param('ulma_pass', self.ulma_pass)
        set_param('ulma_host', self.ulma_host)
        set_param('ulma_port', self.ulma_port)
        set_param('ulma_sid', self.ulma_sid)
        set_param('ulma_database', self.ulma_database)
        set_param('mmmout_table', self.mmmout_table)
        set_param('mmminp_table', self.mmminp_table)
        set_param('fdw', self.fdw)

    def check_extension(self):
        self.env.cr.execute("""select * from pg_extension where extname = '%s'""" % (self.fdw))
        if self.env.cr.rowcount:
            self.oracle_extension = True
        else:
            self.oracle_extension = False

    def check_server_link(self):
        self.env.cr.execute("""select * from pg_foreign_server where srvname = '%s'""" % (self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_server = True
        else:
            self.oracle_server = False
    
    def check_tables(self):
        self.env.cr.execute("""select * from information_schema.foreign_tables where foreign_table_name = '%s' and foreign_server_name = '%s'""" % (self.mmmout_table, self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_mmmout = True
        else:
            self.oracle_mmmout = False

        self.env.cr.execute("""select * from information_schema.foreign_tables where foreign_table_name = '%s' and foreign_server_name = '%s'""" % (self.mmminp_table, self.ulma_database))
        if self.env.cr.rowcount:
            self.oracle_mmminp = True
        else:
            self.oracle_mmminp = False
    
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

    
    def create_table_mmmout(self):

        if self.fdw == 'oracle_fdw':
            table_mod = 'TABLE'
        else:
            table_mod = 'table_name'

        ## Create foreign table mmmout
        self.env.cr.execute("""CREATE FOREIGN TABLE mmmout (mmmabclog character varying(1), mmmacccod numeric(9,0), mmmacccolcod numeric(9,0), mmmacp character(1), mmmacpmot character varying(4), 
        mmmalgent character varying(1), mmmalgsal character varying(1), mmmambreg character varying(1), mmmartapi character varying(1), mmmartdes character varying(40), mmmartean character varying(30), 
        mmmartref character varying(16), mmmbatch character varying(9), mmmcanuni numeric(9,0), mmmcmdref character varying(9) NOT NULL, mmmcntdorre character varying(18), 
        mmmcod numeric(9,0) NOT NULL, mmmcritor character varying(20), mmmdesdes character varying(70), mmmdesdir1 character varying(70), mmmdesdir2 character varying(70), 
        mmmdesdir3 character varying(70), mmmdesdir4 character varying(70), mmmdim character varying(4), mmmdisref character varying(9), mmmdorhue character varying(1), 
        mmmentdes character varying(70), mmmentdir1 character varying(70), mmmentdir2 character varying(70), mmmentdir3 character varying(70), mmmentdir4 character varying(70), 
        mmmexpordref character varying(15), mmmexpordfusref character varying(15), mmmfeccad date, mmmgraocu numeric(3,0), mmmges character varying(9) NOT NULL, 
        mmmlot character varying(20), mmmmaxudsdim numeric(9,0), mmmmaxudsdis numeric(9,0), mmmminudsdis numeric(9,0), mmmmomexp date, mmmmomlot character varying(1), 
        mmmnecman character varying(4), mmmpesfin numeric(9,3), mmmpicent character varying(1), mmmpicsal character varying(1), mmmrecmaqref character(10), 
        mmmrecref character varying(15), mmmremdes character varying(70), mmmremdir1 character varying(70), mmmremdir2 character varying(70), 
        mmmremdir3 character varying(70), mmmremdir4 character varying(70), mmmres character varying(9), mmmresmsj character varying(80), mmmsecada numeric(9,0), 
        mmmsecdis numeric(9,0), mmmsesid numeric(9,0), mmmsorrut character varying(30), mmmterproref character varying(16), mmmterref character varying(16), 
        mmmtolpes numeric(2,0), mmmtrades character varying(70), mmmtraref character varying(16), mmmubichkref character varying(16), mmmubidesref character varying(16), 
        mmmubioriref character varying(16), mmmurgnte character varying(1), mmmzondesref character varying(4), momcre date, momlec date, mmmmonlot character varying(1), 
        id integer NOT NULL, create_uid integer, write_uid integer, create_date timestamp without time zone, write_date timestamp without time zone, mmmmoexp date, 
        mmmcntdorref character varying(18), mmmcrirot character varying(20)) SERVER %s OPTIONS (%s '%s')""" % (self.ulma_database, table_mod, self.mmmout_table))
    
    def create_table_mmminp(self):

        if self.fdw == 'oracle_fdw':
            table_mod = 'TABLE'
        else:
            table_mod = 'table_name'

        ## Create foreign table mmminp
        self.env.cr.execute("""CREATE FOREIGN TABLE mmminp (mmmacp character varying(1), mmmartref character varying(16), mmmcanuni numeric(9,0), 
        mmmcmdref character varying(9) NOT NULL, mmmcntdorref character varying(18), mmmcod numeric(9,0) NOT NULL, mmmcrirot character varying(20), 
        mmmdisref character varying(9), mmmexpordref character varying(15), mmmges character varying(9) NOT NULL, mmmlot character varying(20), 
        mmmresmsj character varying(80), mmmsecada numeric(9,0), mmmsecdis numeric(9,0), mmmsesid numeric(9,0), mmmubidesref character varying(16), 
        mmmubiorief character varying(16), momcre date, momlec date, mmmacccolcod numeric(9,0), mmmobs character varying(255), mmmexpordfusref character varying(15), 
        mmmpesfin numeric(9,3), mmmacccod numeric(9,0), mmmrecmaqref character(10), mmmacpmot character varying(4), mmmcntdordes character varying(18), 
        mmmcntdordori character varying(18), mmmrecref character varying(15), mmmres character varying(9), mmmerrmsj character varying(80), id integer NOT NULL, 
        create_date timestamp without time zone, write_date timestamp without time zone, create_uid integer, write_uid integer) SERVER %s OPTIONS (%s '%s')""" % (self.ulma_database, table_mod, self.mmminp_table))


    def drop_tables(self):
        ## Deletes the tables
        self.env.cr.execute("""DROP FOREIGN TABLE %s""" % (self.mmmout_table))
        self.env.cr.execute("""DROP FOREIGN TABLE %s""" % (self.mmminp_table))
