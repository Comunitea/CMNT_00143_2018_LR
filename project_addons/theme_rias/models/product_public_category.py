# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
 
class productPublicCategory(models.Model):
    _inherit = ["product.public.category"]
     
    website_published = fields.Boolean("Website Published",default=True)
    
    

