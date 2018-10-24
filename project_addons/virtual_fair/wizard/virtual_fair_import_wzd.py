
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from lxml import etree


class VirtualFair(models.TransientModel):

    _name = 'virtual.fair.import.wzd'

    file = fields.Binary(string='File', required=True)
    fair_filename = fields.Char(string='Fair Filename')

    @api.multi
    def import_fair(self):
        self.ensure_one()
        import ipdb; ipdb.set_trace()
