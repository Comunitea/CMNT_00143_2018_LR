 
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class CloseCampaignWzd(models.TransientModel):
    _name = 'close.campaign.wzd' 

    @api.multi
    def close_campaign(self):
        orders = self.env['sale.order'].browse(self._context['active_ids'])
        orders.get_campaign_payment_term()