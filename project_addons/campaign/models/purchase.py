
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class PurchaseOeder(models.Model):

    _inherit = 'purchase.order'

    campaign_id = fields.Many2one('campaign', 'Campaign')

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.campaign_id:
            self.onchange_campaign_id()
        return res
    
    @api.onchange('campaign_id')
    def onchange_campaign_id(self):
        if self.supplier_id:
            domain = [
                ('campaign_id', '=', self.campaign_id.id),
                ('supplier_id', '=', self.partner_id.id),
            ]
            line = self.env['campaign.supplier.line'].search(domain, limit=1)
            if line:
                self.payment_term_id = line.payment_term_id.id
        return res


class PurchaseOederLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.multi
    def get_article_line(self):
        self.ensure_one()
        domain = [
            ('campaign_id', '=', self._context.get('campaign_id')),
            ('supplier_id', '=', self.order_id.partner_id.id),
            ('product_id', '=', self.product_id.id)
        ]
        return self.env['campaign.article.line'].search(domain, limit=1)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super().onchange_product_id()
        if self._context.get('campaign_id'):
            article_line = self.get_article_line()
            if article_line:
                self.price_unit = article_line.purchase_price
        return res