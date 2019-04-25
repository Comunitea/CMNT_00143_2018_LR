
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, 
                count=False, access_rights_uid=None):
        """
        Si campaña está en contexto, devolver solo los productos de la campaña
        """
        if self._context.get('campaign_id', False):
            camp = self.env['campaign'].browse(self._context['campaign_id'])
            product_ids = camp.article_ids.mapped('product_id').ids
            args = [['id', 'in', product_ids]]
        return super(ProductProduct, self)._search(
            args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)
