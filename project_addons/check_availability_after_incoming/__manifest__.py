# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Check availability after incoming moves",
    "version": "11.0.0",
    "category": "Warehouse",
    "website": "http://comunitea.com",
    "author": "Comunitea Servicios Tecnológicos, S.L.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "queue_job",
    ],
    "data": [
        'views/stock_location_views.xml',
        'views/stock_picking.xml',
        'views/res_config_views.xml'
    ],
}
