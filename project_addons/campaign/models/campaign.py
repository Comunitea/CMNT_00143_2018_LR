
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class Campaign(models.Model):

    _name = 'campaign'

    name = fields.Char('Name', required=True)
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    supplier_ids = fields.One2many(comodel_name='campaign.supplier.line',
                                   inverse_name='campaign_id', 
                                   string='Suppliers')
    article_ids = fields.One2many(comodel_name='campaign.article.line',
                                   inverse_name='campaign_id', 
                                   string='Suppliers')
    articles_count = fields.Integer('# Articles',
                                    compute='_count_articles')
    pricelist_id = fields.Many2one('product.pricelist', 'Sale pricelist')
    
    # Supplier dates
    purchases_start_date = fields.Date(string='Purchases Start Date')
    purchases_end_date = fields.Date(string='Purchases End Date')
    
    # Customer terms
    web_publication_date = fields.Date(string='Web Publication Date')
    days_publication = fields.Integer('Validity Days', default=15)
    sale_prices_date = fields.Date(string='Sale prices Date')
    days_prices = fields.Integer('Validity Sale Prices', default=30)

    @api.multi
    def _count_articles(self):
        for campaign in self:
            campaign.articles_count = len(campaign.article_ids)


class CampaignSupplierLines(models.Model):
    _name = 'campaign.supplier.line'

    campaign_id = fields.Many2one('campaign', 'Campaign', required=True)  
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    purchases_start_date = fields.Date(string='Purchases Start Date')
    purchases_end_date = fields.Date(string='Purchases End Date')
    payment_term_id = fields.Many2one('account.payment.term', 'Payment term')

    @api.multi
    @api.depends('campaign_id', 'supplier_id')
    def name_get(self):
        res = []
        for record in self:
            name = '[' + record.campaign_id.name + ']'
            if record.supplier_id:
                name += ' ' + record.supplier_id.name
            res.append((record.id, name))
        return res


class CampaignProductLine(models.Model):
    _name = 'campaign.article.line'

    campaign_id = fields.Many2one('campaign', 'Campaign', required=True)
    supplier_id = fields.Many2one(
        'res.partner', 'Supplier')
    product_id = fields.Many2one('product.product', 'Product')
    campaign_code = fields.Char('Campaign Reference', index=True)
    purchase_price = fields.Float(
        'Supplier Price', digits=dp.get_precision('Product Price'))
    price = fields.Float(
        'Campaign Price', digits=dp.get_precision('Product Price'))
    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'), 
        default=0.0)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.update_pricelist_prices()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        self.update_pricelist_prices()
        return res
    
    @api.multi
    def unlink(self):
        self.unlink_pricelist_prices()
        res = super().unlink()
        return res
    
    @api.multi
    def get_exisiting_item(self):
        res = self.env['product.pricelist.item']
        self.ensure_one()
        domain = [
                ('pricelist_id', '=', self.campaign_id.pricelist_id.id),
                ('product_id', '=', self.product_id.id),
                ('applied_on', '=', '0_product_variant'),
                ('compute_price', '=', 'fixed'),
            ]
        item = self.env['product.pricelist.item'].search(domain, limit=1)
        if item:
            res = item
        return res


    @api.multi
    def update_pricelist_prices(self):
        for line in self:
            item = line.get_exisiting_item()
            if not item:
                vals = {
                    'pricelist_id': line.campaign_id.pricelist_id.id,
                    'product_id': line.product_id.id,
                    'applied_on': '0_product_variant',
                    'compute_price': 'fixed',
                    'fixed_price': line.price,
                    'date_start': self.campaign_id.date_start,
                    'date_end': self.campaign_id.date_end
                }
                self.env['product.pricelist.item'].create(vals)
            else:
                # ? Escribir date_start date end?
                item.write({'fixed_price': line.price})
        return
    
    @api.multi
    def unlink_pricelist_prices(self):
        for line in self:
            item = line.get_exisiting_item()
            if item:
                item.unlink()
        return

