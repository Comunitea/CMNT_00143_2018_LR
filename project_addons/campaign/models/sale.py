
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    campaign_id = fields.Many2one('campaign', 'Campaign')

    @api.onchange('campaign_id')
    def onchange_campaign_id(self):
        self.ensure_one()
        self.pricelist_id = self.campaign_id.pricelist_id.id



class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    def get_article_line(self):
        self.ensure_one()
        domain = [
            ('campaign_id', '=', self._context.get('campaign_id')),
            ('product_id', '=', self.product_id.id)
        ]
        return self.env['campaign.article.line'].search(domain, limit=1)

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        res = super()._onchange_discount()
        if self._context.get('campaign_id'):
            article_line = self.get_article_line()
            if article_line:
                self.discount = article_line.discount
        return res