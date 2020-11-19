# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Supplier pricelist xls import",
    "version": "11.0.1.0.0",
    "summary": "",
    "category": "Purchase",
    "author": "Comunitea",
    "maintainer": "Comunitea",
    "website": "www.comunitea.com",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "external_dependencies": {"python": ["pandas"]},
    "data": [
        "wizard/supplier_pricelist_importer.xml",
        "views/res_partner.xml",
        "security/ir.model.access.csv",
        "views/product.xml",
        "views/product_supplierinfo.xml",
    ],
}
