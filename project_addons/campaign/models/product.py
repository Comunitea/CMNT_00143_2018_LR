
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """
        El super puede devolver todos los productos a comprar o aquellos
        asignados al proveedor (por el modulo purchase_allowed_workflow)
        Si solo la campaña está en contexto, devolver solo los productos de 
        la campaña, si ademñas también esta marcado lo de restringir los
        productos devolver la interseccion de ambos conjuntos.
        """
        res = super(ProductProduct, self).search(
            args, offset=offset, limit=limit, order=order, count=count)

        restrict = self._context.get('use_only_supplied_product', False)
        campaign_products = self.env['product.product']
        if self._context.get('campaign_id', False):
            camp = self.env['campaign'].browse(self._context['campaign_id'])
            campaign_products = camp.article_ids.mapped('product_id')
            if not restrict:
                return campaign_products
            res = res & campaign_products
        return res
