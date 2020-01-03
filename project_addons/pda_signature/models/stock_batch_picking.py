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

from odoo import models, fields, api, _

class StockBatchPicking(models.Model):

    _inherit = 'stock.batch.picking'

    digital_signature = fields.Binary(
        string='Signature',
        oldname="signature_image",
    )
    signature_firstName = fields.Char('First name')
    signature_lastName = fields.Char('Last name')
    signature_email = fields.Char('E-mail')
    signature_location = fields.Char('Location')
    signature_error = fields.Char('Signature error')
    signature_image_data = fields.Char('Signature image data')
    signature_is_signed = fields.Boolean('Is signed')
    signature_pad_info = fields.Char('Pad info')
    signature_raw_data = fields.Char('Raw data')
    signature_sig_string = fields.Char('Sig String')

    @api.multi
    def send_to_signature_pda(self):
        self.ensure_one()
        pass

    @api.multi
    def save_pda_data(self, args):
        for batch in self:
            batch.sudo().update(args)