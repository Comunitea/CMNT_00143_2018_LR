# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError
from ast import literal_eval
from pprint import pprint

import os

ODOO_READ_FOLDER = 'Send'
ODOO_END_FOLDER = 'Receive'
ODOO_WRITE_FOLDER = 'temp'

class ConfigPathFiles(models.TransientModel):

    _inherit = 'res.config.settings'

    path_files = fields.Char('Files Path', help="Path to SGA Adaia exchange files. Must content in, out, error, processed and history folders\nAlso a scheduled action is created: Archive SGA files")
    
    @api.model
    def get_values(self):
        ICP =self.env['ir.config_parameter']
        res = super(ConfigPathFiles, self).get_values()
        pf = ICP.get_param('path_files','False')
        res.update(path_files=pf)
        return res

    @api.multi
    def set_values(self):
        super(ConfigPathFiles, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('path_files', self.path_files)
    
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