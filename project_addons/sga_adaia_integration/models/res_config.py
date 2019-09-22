# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError
from ast import literal_eval

import os

ADAIA_PARAMS = ['path_files', 'adaia_partner_code', 'adaia_partner_prefix', 'adaia_product_code', 'adaia_product_prefix',
 'adaia_product_template_code', 'adaia_product_template_prefix', 'adaia_barcode_code', 'adaia_barcode_prefix', 'adaia_stock_code', 'adaia_stock_prefix',
 'adaia_stock_picking_in', 'adaia_stock_picking_out']

SGA_STATES = [('no_integrated', 'Sin integracion'),
              ('no_send', 'No enviado'),
              ('pending', 'Pendiente Sga'),
              ('export_error', 'Error en exportacion'),
              ('import_error', 'Error en importacion'),
              ('done', 'Realizado'),
              ('cancel', 'Cancelado')]

ODOO_READ_FOLDER = 'Send'
ODOO_END_FOLDER = 'Receive'
ODOO_WRITE_FOLDER = 'temp'

class ConfigAdaiaData(models.TransientModel):

    _inherit = 'res.config.settings'

    path_files = fields.Char('Files Path', help="Path to SGA Adaia exchange files. Must content in, out, error, processed and history folders\nAlso a scheduled action is created: Archive SGA files")
    adaia_partner_code = fields.Char(string="Partner SGA Code", help="SGA Adaia partner file code")
    adaia_product_code = fields.Char(string="Product SGA Code", help="SGA Adaia product file code.")
    adaia_product_template_code = fields.Char(string="Product template SGA Code", help="SGA Adaia product file code.")
    adaia_barcode_code = fields.Char(string="Barcode SGA Code", help="SGA Adaia barcode file code.")
    adaia_stock_code = fields.Char(string="Product stock SGA Code", help="SGA Adaia stock file code.")
    adaia_stock_picking_in = fields.Char(string="Stock picking IN SGA Code", help="SGA Adaia stock picking in file code.")
    adaia_stock_picking_out = fields.Char(string="Stock picking IN SGA Code", help="SGA Adaia stock picking in file code.")
    adaia_partner_prefix = fields.Char(string="Partner SGA prefix", help="SGA Adaia partner file prefix")
    adaia_product_prefix = fields.Char(string="Product SGA prefix", help="SGA Adaia product file prefix.")
    adaia_product_template_prefix = fields.Char(string="Product template SGA prefix", help="SGA Adaia product file prefix.")
    adaia_barcode_prefix = fields.Char(string="Barcode SGA prefix", help="SGA Adaia barcode file prefix.")
    adaia_stock_prefix = fields.Char(string="Product stock SGA prefix", help="SGA Adaia stock file prefix.")
    

    @api.model
    def get_values(self):
        ICP =self.env['ir.config_parameter'].sudo()
        res = super(ConfigAdaiaData, self).get_values()
        for param in ADAIA_PARAMS:
            value= ICP.get_param('sga_adaia_integration.{}'.format(param), False)
            res.update({param: value})
        print (res)
        return res

    @api.multi
    def set_values(self):
        super(ConfigAdaiaData, self).set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        for param in ADAIA_PARAMS:
            ICP.set_param('sga_adaia_integration.{}'.format(param), self[param])
    
    @api.onchange('path_files')
    def on_change_path_files(self):
        if os.path.isdir(self.path_files):
            try:
                for folder in (ODOO_READ_FOLDER, ODOO_WRITE_FOLDER, ODOO_END_FOLDER, 'error', 'archive', 'zip', 'delete', 'log'):
                    new_path = "%s/%s" % (self.path_files, folder)
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
            except:
                raise UserError("Error creating directories in %s" % self.path_files)            
        else:
            if not os.path.exists(self.path_files):
                os.makedirs(self.path_files)
                try:
                    for folder in (ODOO_READ_FOLDER, ODOO_WRITE_FOLDER, ODOO_END_FOLDER, 'error', 'archive', 'zip', 'delete', 'log'):
                        new_path = "%s/%s" % (self.path_files, folder)
                        if not os.path.exists(new_path):
                            os.makedirs(new_path)
                except:
                    raise UserError("Error creating directories in %s" % self.path_files)