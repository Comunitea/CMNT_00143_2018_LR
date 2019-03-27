# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AecocClassification(models.Model):

    _name = 'aecoc.classification'
    _description = "AECOC Classification"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _rec_name = 'complete_name'
    _order = 'parent_left'

    name = fields.Char('Name', index=True, required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_id = fields.Many2one('aecoc.classification', 'Parent Level',
                                index=True, ondelete='cascade')
    child_id = fields.One2many(
        'aecoc.classification', 'parent_id', 'Child Categories')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    product_count = fields.Integer(
        '# Products', compute='_compute_product_count',
        help="Nº products under this AECOC Level "
             "No children levels considered")
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for level in self:
            if level.parent_id:
                level.complete_name = '%s / %s' % \
                    (level.parent_id.complete_name, level.name)
            else:
                level.complete_name = level.name


    def _compute_product_count(self):
        domain = [('aecoc_id', 'child_of', self.ids)]
        read_group_res = self.env['product.template'].read_group(
            domain, ['aecoc_id'], ['aecoc_id'])
        group_data = dict((data['aecoc_id'][0], data['aecoc_id_count'])
            for data in read_group_res)
        for aecoc in self:
            product_count = 0
            for sub_aecoc_id in aecoc.search([('id', 'child_of', aecoc.id)]).ids:
                product_count += group_data.get(sub_aecoc_id, 0)
            aecoc.product_count = product_count

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(
                _('Error ! You cannot create recursive AECOC levels.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]