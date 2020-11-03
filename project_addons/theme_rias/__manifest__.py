# -*- coding: utf-8 -*-
#
##############################################################################
#
#    License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#    © 2019 Comunitea - Ruben Seijas <ruben@comunitea.com>
#    © 2019 Comunitea - Pavel Smirnov <pavel@comunitea.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Las Rías website theme',
    'version': '11.0.0.0.1',
    'summary': 'Customization for Las Rías website',
    'description': '',
    'category': 'Theme',
    'author': 'Comunitea',
    'website': 'http://www.comunitea.com',
    'license': 'AGPL-3',
    'contributors': [
        'Pavel Smirnov <pavel@comunitea.com>',
        'Vicente Ángel Gutiérrez <vicente@comunitea.com>',
        'Rubén Seijas <ruben@comunitea.com>',
    ],
    'depends': [
        # Custom
        'breadcrumbs_base',
        'website_base_rias',
        # OCA
        'website',
        'website_sale',
        'website_slides',
        'website_form',
        'website_sale_hide_empty_category'
    ],
    'data': [
        'data/menu_data.xml',
        'data/page_data.xml',
        'data/slides_data.xml',
        'data/post_data.xml',
        'data/category_data.xml',
        'templates/snippets.xml',
        'templates/head.xml',
        'templates/header.xml',
        'templates/footer.xml',
        'templates/page_home.xml',
        'templates/page_our_shops.xml',
        'templates/page_catalogues.xml',
        'templates/page_about_us.xml',
        'templates/catalogue.xml',
        'templates/blog_post.xml',
        'templates/forms.xml',
        'templates/page_pricelist.xml',
        'views/category.xml',
        'templates/shop.xml'
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
