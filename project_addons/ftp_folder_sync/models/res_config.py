# -*- coding: utf-8 -*-
##############################################################################
#    License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#    Copyright (C) 2019 Comunitea Servicios Tecnológicos S.L. All Rights Reserved
#    Vicente Ángel Gutiérrez <vicente@comunitea.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError
from ftplib import FTP
import os, logging

_logger = logging.getLogger(__name__)

FTP_PARAMS = ['activated', 'ftp_server', 'ftp_login', 'ftp_password', 'ftp_get_folder', 'ftp_sent_folder',
 'local_got_folder', 'local_to_send_folder', 'ftp_port', 'ftp_done_folder', 'local_done_folder',
 'move_local_files', 'move_remote_files', 'delete_remote_files']

class ConfigFTPConnection(models.TransientModel):

    _inherit = 'res.config.settings'

    activated = fields.Boolean('Enviar a SGA')
    ftp_server = fields.Char('Server IP')
    ftp_login = fields.Char(string="Server Login")
    ftp_password = fields.Char(string="Server password")
    ftp_port = fields.Char(string="Server port", help="(Optional)")
    ftp_get_folder = fields.Char(string="Server get folder", help="The folder where you take the files from.")
    ftp_sent_folder = fields.Char(string="Server send folder", help="The folder where you put the files.")
    ftp_done_folder = fields.Char(string="Server done folder", help="The folder where you put the processed files.")
    local_got_folder = fields.Char(string="Local get folder", help="The folder with recieved files.")
    local_to_send_folder = fields.Char(string="Local send folder", help="The folder with files to send.")
    local_done_folder = fields.Char(string="Local done folder", help="The local folder where you put the processed files.")
    move_local_files = fields.Boolean(string="Move done files", help="Move local files on done.")
    move_remote_files = fields.Boolean(string="Move remote done files", help="Move remote files on done.")
    delete_remote_files = fields.Boolean(string="Delete remote done files", help="Delete remote files on done.")

    @api.model
    def get_values(self):
        ICP =self.env['ir.config_parameter'].sudo()
        res = super(ConfigFTPConnection, self).get_values()
        for param in FTP_PARAMS:
            value= ICP.get_param('ftp_folder_sync.{}'.format(param), False)
            res.update({param: value})
        return res

    @api.multi
    def set_values(self):
        super(ConfigFTPConnection, self).set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        for param in FTP_PARAMS:
            ICP.set_param('ftp_folder_sync.{}'.format(param), self[param])

    @api.model
    def sync_folders(self):
        ftp_server = self.env['ir.config_parameter'].get_param('ftp_folder_sync.ftp_server', False)
        ftp_port = self.env['ir.config_parameter'].get_param('ftp_folder_sync.ftp_port', False)
        ftp_login = self.env['ir.config_parameter'].get_param('ftp_folder_sync.ftp_login', False)
        ftp_password = self.env['ir.config_parameter'].get_param('ftp_folder_sync.ftp_password', False)
        
        try:
            _logger.info("Conectando al ftp")
            ftp = FTP()
            ftp.connect(ftp_server, int(ftp_port))
            _logger.info("Conectando al ftp: {}".format(ftp_server))
            ftp.login(ftp_login, ftp_password)
        except Exception as e:
            raise UserError(_('Error: {}').format(e))

        activated = self.env['ir.config_parameter'].get_param('ftp_folder_sync.activated', False)
        if activated:
            self.get_files(ftp)
            ftp.cwd('..')
            self.send_files(ftp)
            ftp.quit()
    
    @api.model
    def get_files(self, ftp):
        local_got_folder = self.env['ir.config_parameter'].get_param('ftp_folder_sync.local_got_folder', False)
        ftp_get_folder = self.env['ir.config_parameter'].get_param('ftp_folder_sync.ftp_get_folder', False)
        ftp_done_folder = self.env['ir.config_parameter'].get_param('ftp_folder_sync.ftp_done_folder', False)
        move_remote_files = self.env['ir.config_parameter'].get_param('ftp_folder_sync.move_remote_files', False)
        delete_remote_files = self.env['ir.config_parameter'].get_param('ftp_folder_sync.delete_remote_files', False)
        ftp.cwd(ftp_get_folder)
        filenames = ftp.nlst()

        _logger.info("Obteniendo ficheros de la carpeta: {}".format(ftp_get_folder))

        try:
            for filename in filenames:
                if filename.startswith('TR'):
                    
                    local_filename = os.path.join(local_got_folder, filename)
                    _logger.info("Descargando archivo: {}".format(filename))

                    done_filename = "../{}/{}".format(ftp_done_folder, filename)
                    local_file = open(local_filename, 'wb')
                    
                    if ftp.retrbinary('RETR '+ filename, local_file.write):
                        _logger.info("Descargado archivo en: {}".format(local_filename))
                        if move_remote_files:
                            ftp.rename(filename, done_filename)
                            _logger.info("Archivo {} movido a: {}".format(filename, done_filename))
                        if delete_remote_files:
                            ftp.delete(filename)
                            _logger.info("Archivo {} borrado".format(filename))
                    local_file.close()
        except Exception as e:
            raise UserError(_('Error: {}').format(e))

    @api.model
    def send_files(self, ftp):
        local_to_send_folder = self.env['ir.config_parameter'].get_param('ftp_folder_sync.local_to_send_folder', False)
        local_done_folder = self.env['ir.config_parameter'].get_param('ftp_folder_sync.local_done_folder', False)
        ftp_sent_folder = self.env['ir.config_parameter'].get_param('ftp_folder_sync.ftp_sent_folder', False)
        move_local_files = self.env['ir.config_parameter'].get_param('ftp_folder_sync.move_local_files', False)
        filenames = [f for f in os.listdir(local_to_send_folder) if os.path.isfile(os.path.join(local_to_send_folder, f))]
        ftp.cwd(ftp_sent_folder)

        _logger.info("Obteniendo ficheros de la carpeta: {}".format(ftp_sent_folder))

        try:
            for filename in filenames:
                local_filename = os.path.join(local_to_send_folder, filename)
                done_filename = "{}/{}".format(local_done_folder, filename)

                _logger.info("Enviando archivo: {}".format(local_filename))
                if ftp.storbinary('STOR '+filename, open(local_filename, 'rb')) and move_local_files:
                    _logger.info("Enviado archivo: {}".format(local_filename))
                    open(local_filename, 'rb').close()
                    os.rename(local_filename, done_filename)
                    _logger.info("Archivo {} movido a: {}".format(local_filename, done_filename))
        except Exception as e:
            raise UserError(_('Error: {}').format(e))

    