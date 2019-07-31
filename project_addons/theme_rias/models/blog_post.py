# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, tools, _


class BlogPost(models.Model):
    _inherit = 'blog.post'

    youtube_link = fields.Char(string="Youtube link")
    youtube_id = fields.Char(compute='compute_video_id')


    @api.depends('youtube_link')
    def compute_video_id(self):
        for post in self:
            if post.youtube_link:
                post.youtube_id = post.youtube_link.split("?v=", 1)[1]
            else:
                post.youtube_id = False


