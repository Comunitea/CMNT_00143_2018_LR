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
    'name': 'Las Rias website base module',
    'version': '1.0',
    'summary': 'Back-end customization for Las Rias website eCommerce',
    'description': '',
    'category': 'Website',
    'author': 'Comunitea',
    'website': 'http://www.comunitea.com',
    'license': 'AGPL-3',
    'contributors': [
        'Pavel Smirnov <pavel@comunitea.com>',
        'Rubén Seijas <ruben@comunitea.com>',
    ],
    'depends': [
        'ecommerce_base',
        'seo_base',
    ],
    'data': [
        'data/website_data.xml',
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
