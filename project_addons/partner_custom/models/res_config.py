# Copyright 2014 Numérigraphe
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from ast import literal_eval

class ResConfigSettings(models.TransientModel):

    """Add options to easily install the submodules"""
    _inherit = 'res.config.settings'


    default_associate_sale_pricelist = fields.Many2one('product.pricelist', company_dependent=True, string="Default pricelist for associates")
    default_no_associate_sale_pricelist = fields.Many2one('product.pricelist', company_dependent=True,
                                                           string="Default pricelist for no associates")


    @api.model
    def get_values(self):
        ICP =self.env['ir.config_parameter']
        res = super(ResConfigSettings, self).get_values()
        dasp = literal_eval(ICP.get_param(
                'default_associate_sale_pricelist','False')
        )
        dnasp = literal_eval(ICP.get_param(
            'default_no_associate_sale_pricelist', 'False')
        )
        res.update(default_associate_sale_pricelist=dasp,default_no_associate_sale_pricelist=dnasp)
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'default_associate_sale_pricelist', self.default_associate_sale_pricelist.id)
        self.env['ir.config_parameter'].set_param(
            'default_no_associate_sale_pricelist', self.default_no_associate_sale_pricelist.id)