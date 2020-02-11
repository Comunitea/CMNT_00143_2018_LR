# -*- coding: utf-8 -*-
# © 2020 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api
from odoo.http import request
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_cart_description = fields.Text('User cart description.')