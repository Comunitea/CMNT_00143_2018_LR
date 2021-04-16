# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from base64 import b64decode
from io import BytesIO
from datetime import date, datetime, time, timedelta

import pandas
from odoo import _, fields, models
from odoo.exceptions import UserError


class SupplierPricelistImporter(models.TransientModel):

    _name = "supplier.pricelist.importer"

    supplier = fields.Many2one("res.partner", required=True)
    valid_from = fields.Date("Valid From", required=True)
    valid_to = fields.Date("Valid To")
    import_file = fields.Binary(required=True)
    log_id = fields.Many2one("log.import.spl")

    def import_pricelist(self):
        def create_supplierinfo(product, unit_price, min_units, discount_group):
            print ("CREA PRECIO")
            self.env["product.supplierinfo"].create(
                {
                    "active": product.active,
                    "name": self.supplier.id,
                    "product_id": product.id,
                    "product_tmpl_id": product.product_tmpl_id.id,
                    "min_qty": min_units,
                    "price": unit_price,
                    "xls_imported": True,
                    'supplier_discount_group_id': discount_group.id,
                    "date_start": self.valid_from,
                    "date_end": self.valid_to,
                    "log_id": self.log_id.id
                }
            )
        log_name = self.supplier.name + " - " + fields.Date.context_today(self)
        self.log_id = self.env['log.import.spl'].create(
            {
                'name': log_name,
                'supplier_id': self.supplier.id
            }
        )
        supplierinfo = self.env["product.supplierinfo"].search(
            [("name", "=", self.supplier.id), ("xls_imported", "=", True)]
        )
        products_to_remove = supplierinfo.mapped("product_id")
        si_no_end = self.env["product.supplierinfo"].search(
            [("name", "=", self.supplier.id), ("date_end", "=", False)])
        date_end = datetime.strftime(datetime.
                                 strptime(self.valid_from,
                                          '%Y-%m-%d') +
                                 timedelta(days=-1),
                                 '%Y-%m-%d')
        si_no_end.write(
            {
                'date_end': date_end
            }
        )
        df = pandas.read_excel(BytesIO(b64decode(self.import_file)))
        discount_groups = df["grupo_dto  o NETO"].values
        for discount_group in set(discount_groups.flatten()):
            if pandas.isnull(discount_group) or not discount_group:
                continue
            discount_group_r = self.supplier.discount_groups.filtered(
                lambda r: r.name == discount_group
            )
            if not discount_group_r:
                raise UserError(
                    _("Discount group {} not found").format(discount_group)
                )
        count = 0
        for line in df.index:
            print("Nueva Linea %d" % count)
            product = False
            wh_product = True
            product_name = df["descripcion (max. 100 caracteres)"][line]
            product_ref = df["ref (max. 40 caracteres)"][line]
            product_ean = df["ean_unitario (13 digitos consecutivos)"][line]
            discount_group = df["grupo_dto  o NETO"][line]
            discount_group_r = self.supplier.discount_groups.filtered(
                lambda r: r.name == discount_group
            )
            if not pandas.isnull(product_ean) and product_ean:
                product_ean = str(int(product_ean))
                product = (
                    self.env["product.product"]
                    .with_context(active_test=False)
                    .search([("barcode", "=", product_ean)])
                )
            if not product:
                product = (
                    self.env["product.product"]
                    .with_context(active_test=False)
                    .search([("default_code", "=", product_ref)])
                )
                if not product:
                    wh_product = False
                    print ("CREA PRODUCTO")
                    product = self.env["product.product"].create(
                        {
                            "name": not pandas.isnull(product_name)
                            and product_name,
                            "default_code": not pandas.isnull(product_ref)
                            and product_ref,
                            "barcode": not pandas.isnull(product_ean)
                            and product_ean,
                            "active": False,
                            "xls_imported": True,
                            "type": "product",
                        }
                    )
                    product.product_tmpl_id.active = False
                else:
                    wh_product = product.active
            uos_factor = df["unidad envase (número natural)"][line]
            uom_factor = df["unidad embalaje (número natural)"][line]
            if pandas.isnull(uos_factor):
                uos_factor = 0
            if pandas.isnull(uom_factor):
                uom_factor = 0
            unit_price = df["precio tarifa"][line]
            factor = df["factor"][line]
            if pandas.isnull(factor) or factor == 0:
                factor = 1

            new_standard_price = (unit_price / factor) * (
                1 - discount_group_r.calculated_discount / 100
            )

            brand = df["MARCA"][line]
            brand_partner_id = None
            if not pandas.isnull(brand) and brand:
                brand_partner_id = (
                    self.env["res.partner"]
                    .search(
                        [
                            ("name", "=", brand),
                            ("parent_id", "=", self.supplier.id),
                        ]
                    )
                    .id
                )

                if not brand_partner_id:
                    raise UserError(
                        _("Brand partner {} not found").format(brand)
                    )
            product.write(
                {
                    "uom_factor": uom_factor,
                    "uos_factor": uos_factor,
                    "standard_price": new_standard_price,
                    "brand_partner": brand_partner_id,
                }
            )
            create_supplierinfo(product, unit_price, 0, discount_group_r)
            if product in products_to_remove:
                products_to_remove -= product
            created_si = False
            for i in range(1, 6):
                qty_tag = "cant_dsd{}".format(i)
                price_tag = "precio{}".format(i)
                if not pandas.isnull(df[qty_tag][line]) and df[qty_tag][line]:
                    unit_price = df[price_tag][line]
                    min_units = df[qty_tag][line]
                    create_supplierinf(product, unit_price, min_units, discount_group_r)
                    created_si = True
            
            count = count + 1
        if products_to_remove:
            self.env.cr.execute(
                "select id from product_product where product_tmpl_id in {}".format(
                    products_to_remove._ids
                )
            )
            product_product_ids = self.env.cr.fetchall()
            product_product_ids = tuple([x[0] for x in product_product_ids])
            self.env.cr.execute(
                "select product_id from purchase_order_line where product_id in {}".format(
                    product_product_ids
                )
            )
            not_remove_products = self.env.cr.fetchall()
            not_remove_products = tuple([x[0] for x in not_remove_products])
            self.env.cr.execute(
                "select product_tmpl_id from product_product where id in {}".format(
                    not_remove_products
                )
            )
            not_remove_products = self.env.cr.fetchall()
            not_remove_products = tuple([x[0] for x in not_remove_products])
            products_to_remove = products_to_remove.filtered(
                lambda r: r.id not in not_remove_products
                and not product.active
                and not product.seller_ids
            )
            products_to_remove.unlink()
