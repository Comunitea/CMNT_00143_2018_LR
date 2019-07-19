# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields

class Menu(models.Model):

    _inherit = "website.menu"

    menu_icon = fields.Char('Icon', default='', help='You can check the full list of icons at https://fontawesome.com/cheatsheet?from=io')
    active = fields.Boolean('Active', default=False, help="Defines if the menu should be active or not.")
