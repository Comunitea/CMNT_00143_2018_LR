
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import UserError
import base64


class VirtualFair(models.TransientModel):

    _name = 'virtual.fair.import.wzd'

    file = fields.Binary(string='File', required=True)
    fair_filename = fields.Char(string='Fair Filename')

    @api.multi
    def import_fair(self):
        self.ensure_one()
        file_data = base64.b64decode(self.file)
        try:
            xml_root = etree.fromstring(file_data)
        except Exception as e:
            raise UserError(_(
                    "This XML file is not XML-compliant. Error: %s") % e)
        date_start = xml_root.get('fDesde')
        date_end = xml_root.get('fHasta')
        name = xml_root.text

        vals = {
            'name': name,
            'date_start': date_start,
            'date_end': date_end,
        }
        fair = self.env['virtual.fair'].create(vals)
        if fair:
            action = self.env.ref('virtual_fair.action_virtual_fair').\
                read()[0]
            form_view_name = 'virtual_fair.view_virtual_fair_form'
            action['views'] = [(self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = fair.id
            return action
        return
