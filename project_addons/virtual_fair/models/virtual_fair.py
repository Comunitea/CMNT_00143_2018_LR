
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class VirtualFair(models.Model):

    _name = 'virtual.fair'

    name = fields.Char('Name')