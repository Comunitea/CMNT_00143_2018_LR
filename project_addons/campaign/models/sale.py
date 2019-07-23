
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
    
    @api.multi
    def get_campaign_payment_term(self):
        for order in self:
            if not order.campaign_id:
              continue
            amount = order.amount_untaxed
            domain = [
                ('campaign_id', '=', order.campaign_id.id),
                ('amount', '<=', amount)
            ]
            st = self.env['section.term'].search(domain, order='amount desc', 
                                                 limit=1)
            if st:
                order.write({'payment_term_id': st.term_id.id})
        return

    @api.multi
    def action_confirm(self):
        self.get_campaign_payment_term()
        return super().action_confirm()

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    campaign_id = fields.Many2one('campaign', 'Campaign')

    @api.onchange('product_id')
    def product_id_change(self):
        """
        If default sales secondary unit set on product, put on secondary
        quantity 1 for being the default quantity. We override this method,
        that is the one that sets by default 1 on the other quantity with that
        purpose.
        """
        res = super(SaleOrderLine, self).product_id_change()
        self.campaign_id = self.order_id.campaign_id
        return res

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