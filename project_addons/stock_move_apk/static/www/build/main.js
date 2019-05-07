webpackJsonp([1],{

/***/ 123:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return StockProvider; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__odoo_odoo__ = __webpack_require__(124);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_ionic_angular__ = __webpack_require__(40);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__ionic_storage__ = __webpack_require__(65);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};




/*
  Generated class for the StockProvider provider.

  See https://angular.io/guide/dependency-injection for more info on providers
  and Angular DI.
*/
var StockProvider = /** @class */ (function () {
    function StockProvider(odooCon, alertCtrl, storage) {
        this.odooCon = odooCon;
        this.alertCtrl = alertCtrl;
        this.storage = storage;
        this.STOCK_FIELDS = {
            'stock.picking.type': {
                'form': ['id', 'name', 'code', 'warehouse_id', 'default_location_src_id', 'default_location_dest_id'],
                'tree': ['id', 'name', 'code', 'warehouse_id', 'default_location_src_id', 'default_location_dest_id']
            },
            'stock.picking': {
                'form': ['id', 'name', 'state', 'partner_id', 'scheduled_date', 'location_id', 'location_dest_id', 'note', 'picking_type_id', 'move_lines'],
                'tree': ['id', 'name', 'state', 'scheduled_date', 'picking_type_id']
            },
            'stock.move': {
                'form': ['id', 'name', 'has_tracking', 'state', 'product_id', 'product_uom', 'picking_id', 'location_id', 'location_dest_id', 'product_uom_qty', 'product_qty', 'display_name', 'need_check', 'need_dest_check', 'inventory_id'],
                'tree': ['id', 'origin', 'product_default_code', 'product_id', 'has_tracking', 'product_uom', 'picking_id', 'product_qty', 'product_uom_qty', 'state', 'location_id', 'location_dest_id'],
                'inview': ['product_id', 'product_uom_qty', 'state'],
                'moves': ['move_dest_ids'],
                'partner': ['partner_id']
            },
            'stock.move.line': {
                'form': ['id', 'move_id', 'state', 'product_id', 'picking_id', 'location_id', 'location_dest_id', 'product_uom_qty', 'lot_id', 'package_id', 'product_qty', 'qty_done', 'result_package_id', 'display_name', 'barcode_dest', 'barcode', 'lot_name', 'ordered_qty', 'need_check', 'need_dest_check', 'original_location_short_name', 'final_location_short_name', 'product_short_name', 'product_barcode', 'product_need_check', 'default_code'],
                'tree': ['id', 'origin', 'name', 'result_package_id', 'move_id', 'product_qty', 'state', 'package_id', 'shipping_type', 'partner_default_shipping_type', 'result_package_shipping_type'],
                'done': ['id', 'qty_done'],
                'partner': ['partner_id', 'partner_default_shipping_type']
            },
            'product.product': {
                'form': ['id', 'default_code', 'barcode', 'product_tmpl_id', 'product_tmpl_name', 'tracking'],
                'tree': ['id', 'default_code', 'barcode']
            },
            'stock.location': {
                'form': ['id', 'complete_name', 'barcode', 'need_dest_check', 'name', 'location_id', 'need_check'],
                'tree': ['need_dest_check'],
                'check': ['need_check']
            },
            'stock.quant': {
                'form': ['id', 'product_id', 'location_id', 'lot_id', 'package_id', 'quantity', 'reserved_quantity', 'product_tracking'],
                'tree': ['id', 'product_id', 'location_id', 'quantity', 'reserved_quantity']
            },
            'stock.quant.package': {
                'form': ['id', 'name', 'mono_product', 'lot_id', 'location_id', 'location_barcode', 'product_id', 'product_short_name', 'product_tracking', 'quant_ids'],
                'tree': ['id', 'name', 'move_line_ids', 'shipping_type', 'delivery_carrier_id', 'partner_default_shipping_type', 'selected_route']
            },
            'stock.inventory': {
                'form': ['name', 'date', 'state', 'location_id', 'filter', 'product_id', 'package_id', 'lot_id', 'category_id', 'line_ids', 'move_ids', 'original_location_short_name', 'original_product_short_name'],
                'tree': ['id', 'name', 'date', 'state']
            },
            'stock.inventory.line': {
                'form': ['inventory_id', 'product_name', 'product_barcode', 'product_default_code', 'location_id', 'package_id', 'prod_lot_id', 'theoretical_qty', 'product_qty', 'original_location_short_name'],
                'tree': ['product_name', 'location_id', 'package_id', 'prodlot_name', 'theoretical_qty', 'product_qty', 'original_location_short_name'],
                'write': ['product_qty']
            },
            'stock.warehouse': {
                'form': ['id', 'name', 'company_id']
            },
            'delivery.carrier': {
                'form': ['id', 'name'],
                'tree': ['id', 'name']
            },
            'stock.location.route': {
                'form': ['id', 'name'],
                'tree': ['id', 'name']
            }
        };
        this.STOCK_STATES = {
            'draf': 'Borrador',
            'waiting': 'Esperando',
            'confirmed': 'En espera',
            'assigned': 'Reservado',
            'partially_available': 'Parcialmente',
            'done': 'Hecho',
            'cancel': 'Cancelado'
        };
        this.STATE_ICONS = {
            'cancel': 'trash',
            'error': 'alert',
            'done': 'checkmark-circle',
            'waiting': 'clock',
            'confirmed': 'checkmark',
            'partially_available': 'checkmark',
            'assigned': 'done-all',
            'draft': 'close-circle'
        };
        console.log('Hello StockProvider Provider');
        this.picking_types = this.get_picking_types([]);
    }
    // Picking Types
    StockProvider.prototype.init_values = function () {
        this.get_picking_types();
    };
    StockProvider.prototype.get_picking_types = function (domain) {
        var _this = this;
        if (domain === void 0) { domain = []; }
        var picking_type_domain = [[]];
        var self = this;
        if (domain) {
            picking_type_domain.push(domain);
        }
        var model = 'stock.picking.type';
        var fields = this.STOCK_FIELDS[model]['form'];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (pt_ids) {
                _this.storage.set('PICKING_TYPES', pt_ids).then(function () {
                    _this.picking_types = pt_ids;
                    resolve(pt_ids);
                });
            })
                .catch(function (err) {
                _this.picking_types = false;
                reject(false);
                console.log("Error buscando " + model);
            });
        });
        return promise;
    };
    StockProvider.prototype.get_current_picking_type = function (id) {
        var self = this;
        var model = 'stock.picking.type';
        var fields = this.STOCK_FIELDS[model]['form'];
        var domain = [['id', '=', id]];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (sp_ids) {
                for (var sm_id in sp_ids) {
                    sp_ids[sm_id]['model'] = model;
                }
                resolve(sp_ids);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error buscando " + model);
            });
        });
        return promise;
    };
    // New package
    StockProvider.prototype.create_new_package = function (model, partner_id, shipping_type) {
        var self = this;
        var pckg_model = model;
        var pckg_values = {
            'dest_partner_id': partner_id,
            'shipping_type': shipping_type
        };
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.new_package(pckg_model, pckg_values).then(function (lineas) {
                resolve(lineas);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error");
            });
        });
        return promise;
    };
    StockProvider.prototype.add_package_id_to_line = function (move_id, result_package_id, shipping_type) {
        if (shipping_type === void 0) { shipping_type = false; }
        var self = this;
        var model = 'stock.move.line';
        var valores = {
            'result_package_id': result_package_id
        };
        if (shipping_type != false) {
            valores['shipping_type'] = shipping_type;
        }
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.update_lines(model, 'write', valores, move_id).then(function (sp_ids) {
                for (var sm_id in sp_ids) {
                    sp_ids[sm_id]['model'] = model;
                }
                resolve(sp_ids);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
            });
        });
        return promise;
    };
    StockProvider.prototype.get_package_info = function (id) {
        var self = this;
        var domain = [['id', '=', id]];
        var model = 'stock.quant.package';
        var fields = this.STOCK_FIELDS[model]['tree'];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (data) {
                for (var sm_id in data) {
                    data[sm_id]['model'] = model;
                }
                resolve(data);
            })
                .catch(function (err) {
                reject(err);
            });
        });
        return promise;
    };
    StockProvider.prototype.get_package_lines = function (package_id) {
        var self = this;
        var model;
        var values = {
            'package': package_id
        };
        model = 'stock.quant.package';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'get_lines_info_apk', values).then(function (done) {
                resolve(done);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
            });
        });
        return promise;
    };
    StockProvider.prototype.get_partner_empty_packages = function (partner_id) {
        var self = this;
        var model;
        var values = {
            'dest_partner_id': partner_id
        };
        model = 'stock.quant.package';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'get_partner_empty_packages', values).then(function (done) {
                resolve(done);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
            });
        });
        return promise;
    };
    StockProvider.prototype.delete_package = function (package_id) {
        var self = this;
        var model;
        var values = {
            'package': package_id
        };
        model = 'stock.quant.package';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'delete_package_from_apk', values).then(function (done) {
                resolve(done);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
            });
        });
        return promise;
    };
    StockProvider.prototype.set_package_info = function (package_id, valores) {
        var self = this;
        var model = 'stock.quant.package';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.update_lines(model, 'write', valores, package_id).then(function (sp_ids) {
                for (var sm_id in sp_ids) {
                    sp_ids[sm_id]['model'] = model;
                }
                resolve(sp_ids);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
            });
        });
        return promise;
    };
    StockProvider.prototype.set_package_shipping_type = function (values) {
        var self = this;
        var model;
        model = 'stock.quant.package';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'change_shipping_type', values).then(function (done) {
                resolve(done);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
            });
        });
        return promise;
    };
    // Home warehouse selection
    StockProvider.prototype.get_available_warehouse_info = function (company_ids, type) {
        if (type === void 0) { type = 'form'; }
        var self = this;
        var model = 'stock.warehouse';
        var domain = [['company_id', 'in', company_ids]];
        var fields = this.STOCK_FIELDS[model][type];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (sp_ids) {
                for (var sm_id in sp_ids) {
                    sp_ids[sm_id]['model'] = model;
                }
                resolve(sp_ids);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error buscando " + model);
            });
        });
        return promise;
    };
    // Move lines
    StockProvider.prototype.get_stock_move_list = function (domain, type) {
        if (type === void 0) { type = 'tree'; }
        var self = this;
        var model = 'stock.move';
        var fields = this.STOCK_FIELDS[model][type];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (sp_ids) {
                for (var sm_id in sp_ids) {
                    sp_ids[sm_id]['model'] = model;
                }
                resolve(sp_ids);
            })
                .catch(function (err) {
                console.log(err);
                reject(false);
                console.log("Error buscando " + model);
            });
        });
        return promise;
    };
    StockProvider.prototype.get_stock_move_lines_list_apk = function (partner_id, location_dest_id) {
        var self = this;
        var model;
        var values = {
            'location_dest_id': location_dest_id,
            'partner_id': partner_id
        };
        model = 'stock.move.line';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'get_stock_move_lines_list_apk', values).then(function (done) {
                resolve(done);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
            });
        });
        return promise;
    };
    StockProvider.prototype.get_stock_move_lines_list = function (domain, type) {
        if (type === void 0) { type = 'tree'; }
        var self = this;
        var model = 'stock.move.line';
        var fields = this.STOCK_FIELDS[model][type];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (sp_ids) {
                for (var sm_id in sp_ids) {
                    sp_ids[sm_id]['model'] = model;
                }
                resolve(sp_ids);
            })
                .catch(function (err) {
                console.log(err);
                reject(false);
                console.log("Error buscando " + model);
            });
        });
        return promise;
    };
    StockProvider.prototype.get_move_line_info = function (id) {
        var self = this;
        var domain = [['id', '=', id]];
        var model = 'stock.move.line';
        var fields = this.STOCK_FIELDS[model]['tree'];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (data) {
                for (var sm_id in data) {
                    data[sm_id]['model'] = model;
                }
                resolve(data);
            })
                .catch(function (err) {
                reject(err);
            });
        });
        return promise;
    };
    StockProvider.prototype.set_move_line_info = function (move_id, valores) {
        var self = this;
        var model = 'stock.move.line';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.update_lines(model, 'write', valores, move_id).then(function (sp_ids) {
                for (var sm_id in sp_ids) {
                    sp_ids[sm_id]['model'] = model;
                }
                resolve(sp_ids);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
            });
        });
        return promise;
    };
    // Users list
    StockProvider.prototype.get_users_list = function (domain, type) {
        if (type === void 0) { type = 'partner'; }
        var self = this;
        var model = 'stock.move';
        var fields = this.STOCK_FIELDS[model][type];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (sp_ids) {
                resolve(sp_ids);
            })
                .catch(function (err) {
                console.log(err);
                reject(false);
                console.log("Error buscando " + model);
            });
        });
        return promise;
    };
    StockProvider.prototype.get_users_list_for_apk = function (location_dest_id) {
        var self = this;
        var model;
        var values = {
            'location_dest_id': location_dest_id
        };
        model = 'stock.move';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'get_users_list_for_apk', values).then(function (done) {
                resolve(done);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
            });
        });
        return promise;
    };
    // Alerts
    StockProvider.prototype.presentAlert = function (titulo, texto) {
        var alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok'],
        });
        alert.present();
    };
    StockProvider.prototype.errorAlert = function (model, move_id, data) {
        var subtitulo = 'No se ha podido guardar en el id ' + move_id + ' del modelo ' + model + ' el valor: ' + data;
        var alertError = this.alertCtrl.create({
            title: 'Error',
            subTitle: subtitulo,
            buttons: ['OK']
        });
        alertError.present();
    };
    // Delivery carriers
    StockProvider.prototype.get_delivery_carriers = function (domain) {
        var self = this;
        var model = 'delivery.carrier';
        var type = 'tree';
        var fields = this.STOCK_FIELDS[model][type];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (sp_ids) {
                resolve(sp_ids);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error buscando " + model);
            });
        });
        return promise;
    };
    // Routes
    StockProvider.prototype.get_routes = function (domain) {
        var self = this;
        var model = 'stock.location.route';
        var type = 'tree';
        var fields = this.STOCK_FIELDS[model][type];
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.search_read(model, domain, fields, 0, 0).then(function (sp_ids) {
                resolve(sp_ids);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error buscando " + model);
            });
        });
        return promise;
    };
    StockProvider = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["A" /* Injectable */])(),
        __metadata("design:paramtypes", [__WEBPACK_IMPORTED_MODULE_1__odoo_odoo__["a" /* OdooProvider */], __WEBPACK_IMPORTED_MODULE_2_ionic_angular__["b" /* AlertController */], __WEBPACK_IMPORTED_MODULE_3__ionic_storage__["b" /* Storage */]])
    ], StockProvider);
    return StockProvider;
}());

//# sourceMappingURL=stock.js.map

/***/ }),

/***/ 124:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return OdooProvider; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__ionic_storage__ = __webpack_require__(65);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


var OdooProvider = /** @class */ (function () {
    function OdooProvider(storage) {
        this.storage = storage;
        this.context = { 'lang': 'es_ES' };
        this.uid = 0;
    }
    OdooProvider.prototype.login = function (user, password) {
        var _this = this;
        var self = this;
        var promise = new Promise(function (resolve, reject) {
            self.storage.get('CONEXION').then(function (con_data) {
                var odoo = new OdooApi(con_data.url, con_data.db);
                // this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
                if (con_data == null) {
                    var err = { 'title': 'Error!', 'msg': 'No hay datos para establecer la conexión' };
                    reject(err);
                }
                else {
                    odoo.login(con_data.username, con_data.password).then(function (uid) {
                        con_data['uid'] = uid;
                        _this.storage.set('CONEXION', con_data).then(function () {
                            self.uid = uid;
                            resolve(uid);
                        });
                    })
                        .catch(function (mierror) {
                        var err = { 'title': 'Error!', 'msg': 'No se pudo conectar con Odoo' };
                        reject(err);
                    });
                }
            });
        });
        return promise;
    };
    OdooProvider.prototype.search_read = function (model, domain, fields, offset, limit, order) {
        var _this = this;
        if (offset === void 0) { offset = 0; }
        if (limit === void 0) { limit = 0; }
        if (order === void 0) { order = ''; }
        var promise = new Promise(function (resolve, reject) {
            _this.storage.get('CONEXION').then(function (con_data) {
                if (con_data == null) {
                    var err = { 'title': 'Error!', 'msg': 'No hay datos para establecer la conexión' };
                    reject(err);
                }
                else {
                    var odoo = new OdooApi(con_data.url, con_data.db, con_data);
                    odoo.search_read(model, domain, fields, offset, limit, order).then(function (res) {
                        resolve(res);
                    })
                        .catch(function () {
                        var err = { 'title': 'Error!', 'msg': 'Fallo al llamar al hacer search_read' };
                        reject(err);
                    });
                }
            });
        });
        return promise;
    };
    OdooProvider.prototype.execute = function (model, method, values) {
        var self = this;
        var promise = new Promise(function (resolve, reject) {
            self.storage.get('CONEXION').then(function (con_data) {
                var odoo = new OdooApi(con_data.url, con_data.db);
                odoo.context = self.context;
                if (con_data == null) {
                    var err = { 'title': 'Error!', 'msg': 'No hay datos para establecer la conexión' };
                    reject(err);
                }
                else {
                    odoo.login(con_data.username, con_data.password).then(function (uid) {
                        odoo.call(model, method, values).then(function (res) {
                            resolve(res);
                        })
                            .catch(function (error) {
                            var err = { 'title': 'Error!', 'msg': 'Fallo al llamar al método ' + method + ' del modelo app.regustry' };
                            reject(err);
                        });
                    })
                        .catch(function () {
                        var err = { 'title': 'Error!', 'msg': 'No se pudo conectar con Odoo' };
                        reject(err);
                    });
                }
            });
        });
        return promise;
    };
    OdooProvider.prototype.update_lines = function (model, method, values, domain) {
        var self = this;
        var promise = new Promise(function (resolve, reject) {
            self.storage.get('CONEXION').then(function (con_data) {
                var odoo = new OdooApi(con_data.url, con_data.db);
                odoo.context = self.context;
                if (con_data == null) {
                    var err = { 'title': 'Error!', 'msg': 'No hay datos para establecer la conexión' };
                    reject(err);
                }
                else {
                    odoo.login(con_data.username, con_data.password).then(function (uid) {
                        odoo.write(model, domain, values).then(function (res) {
                            resolve(res);
                        })
                            .catch(function () {
                            var err = { 'title': 'Error!', 'msg': 'Fallo al llamar al método ' + method + ' del modelo app.registry' };
                            reject(err);
                        });
                    })
                        .catch(function () {
                        var err = { 'title': 'Error!', 'msg': 'No se pudo conectar con Odoo' };
                        reject(err);
                    });
                }
            });
        });
        return promise;
    };
    OdooProvider.prototype.quants_pda_check = function (model, method, values) {
        var self = this;
        var promise = new Promise(function (resolve, reject) {
            self.storage.get('CONEXION').then(function (con_data) {
                var odoo = new OdooApi(con_data.url, con_data.db);
                odoo.context = self.context;
                if (con_data == null) {
                    var err = { 'title': 'Error!', 'msg': 'No hay datos para establecer la conexión' };
                    reject(err);
                }
                else {
                    odoo.login(con_data.username, con_data.password).then(function (uid) {
                        odoo.call(model, method, values).then(function (res) {
                            resolve(res);
                        })
                            .catch(function (error) {
                            console.log(error);
                            var err = { 'title': 'Error!', 'msg': 'Fallo al llamar al método ' + method + 'del modelo app.regustry' };
                            reject(err);
                        });
                    })
                        .catch(function () {
                        var err = { 'title': 'Error!', 'msg': 'No se pudo conectar con Odoo' };
                        reject(err);
                    });
                }
            });
        });
        return promise;
    };
    OdooProvider.prototype.new_package = function (model, values) {
        var self = this;
        var promise = new Promise(function (resolve, reject) {
            self.storage.get('CONEXION').then(function (con_data) {
                var odoo = new OdooApi(con_data.url, con_data.db);
                odoo.context = self.context;
                if (con_data == null) {
                    var err = { 'title': 'Error!', 'msg': 'No hay datos para establecer la conexión' };
                    reject(err);
                }
                else {
                    odoo.login(con_data.username, con_data.password).then(function (uid) {
                        odoo.create(model, values).then(function (res) {
                            resolve(res);
                        })
                            .catch(function (error) {
                            console.log(error);
                            var err = { 'title': 'Error!', 'msg': 'Fallo al llamar al método' };
                            reject(err);
                        });
                    })
                        .catch(function () {
                        var err = { 'title': 'Error!', 'msg': 'No se pudo conectar con Odoo' };
                        reject(err);
                    });
                }
            });
        });
        return promise;
    };
    OdooProvider = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["A" /* Injectable */])(),
        __metadata("design:paramtypes", [__WEBPACK_IMPORTED_MODULE_1__ionic_storage__["b" /* Storage */]])
    ], OdooProvider);
    return OdooProvider;
}());

//# sourceMappingURL=odoo.js.map

/***/ }),

/***/ 149:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return StockMoveListPage; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_ionic_angular__ = __webpack_require__(40);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__providers_stock_stock__ = __webpack_require__(123);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__ionic_storage__ = __webpack_require__(65);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_rxjs__ = __webpack_require__(35);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_ng2_dragula__ = __webpack_require__(227);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};






/**
 * Generated class for the StockMoveListPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */
var StockMoveListPage = /** @class */ (function () {
    function StockMoveListPage(alertCtrl, actionSheetCtrl, dragulaService, navCtrl, navParams, viewCtrl, storage, stockInfo, changeDetectorRef) {
        var _this = this;
        this.alertCtrl = alertCtrl;
        this.actionSheetCtrl = actionSheetCtrl;
        this.dragulaService = dragulaService;
        this.navCtrl = navCtrl;
        this.navParams = navParams;
        this.viewCtrl = viewCtrl;
        this.storage = storage;
        this.stockInfo = stockInfo;
        this.changeDetectorRef = changeDetectorRef;
        this.subs = new __WEBPACK_IMPORTED_MODULE_4_rxjs__["Subscription"]();
        this.move_state_filter = 0;
        this.passed_selected_partner = this.navParams.data.current_selected_partner;
        this.passed_selected_pkg = this.navParams.data.current_selected_pkg;
        this.passed_shipping_type = this.navParams.data.current_shipping_type;
        this.move_status = [];
        this.users_list = [];
        this.full_users_list = [];
        this.filtered_users_ids = [];
        this.current_pkg_info = [];
        this.current_partner_pkg_list = [];
        this.current_selected_pkg = [];
        this.filtered_pkg_list = [];
        this.full_line_ids = [];
        this.current_selected_partner = [];
        this.selected_pkg_current_shipping_type = false;
        this.selected_partner_name = false;
        this.selected_pkg_default_shipping = false;
        this.selected_pkg_selected_shipping = false;
        this.selected_pkg_delivery_carrier_id = false;
        this.selected_pkg_selected_route_id = false;
        this.current_list_shown = false;
        this.selected_partner_default_shipping_type = false;
        this.current_shipping_type = false;
        this.current_partner_arrival_pkgs_list = [];
        this.filtered_arrival_pkg_list = [];
        this.selected_line_default_shipping = [];
        this.selected_line_selected_shipping = [];
        this.move_status[0] = {
            'id': 0,
            'code': 'assigned',
            'name': 'Reservado',
            'index': 0
        };
        this.get_owner_id();
        // Dragula //
        this.subs.add(this.dragulaService.dropModel()
            .subscribe(function (_a) {
            var el = _a.el, target = _a.target, source = _a.source;
            if (target.id == "pkgs" && source.id == "lines") {
                _this.create_new_package(parseInt(el.id));
            }
            else if (target.id == "pkgs_info" && source.id == "lines") {
                _this.add_product_to_package(parseInt(el.id));
            }
            else if (target.id == "pkgs_info" && source.id == "arrival_pkgs") {
                _this.add_package_content_to_package(parseInt(el.id));
            }
        }));
        this.subs.add(this.dragulaService.removeModel()
            .subscribe(function (_a) {
            var el = _a.el, source = _a.source;
            if (source.id == "pkgs") {
                _this.showDestroyConfirmation(parseInt(el.id));
            }
            else if (source.id == "pkgs_info") {
                _this.remove_product_from_pkg(parseInt(el.id));
            }
            else if (source.id == "lines" || source.id == "arrival_pkgs") {
                _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg);
            }
        }));
        dragulaService.destroy("move_lines_container");
        dragulaService.createGroup("move_lines_container", {
            removeOnSpill: true,
            accepts: function (el, target, source, sibling) {
                // Para que no se puedan arrastrar otras líneas al contenedor.
                if (source.id == 'lines' && target.id == 'pkgs') {
                    return true;
                }
                else if (source.id == 'lines' && _this.current_selected_pkg && target.id == 'pkgs_info') {
                    return true;
                }
                else if (source.id == 'arrival_pkgs' && _this.current_selected_pkg && target.id == 'pkgs_info') {
                    return true;
                }
            }
        });
    }
    StockMoveListPage_1 = StockMoveListPage;
    StockMoveListPage.prototype.showDestroyConfirmation = function (package_id) {
        var _this = this;
        var confirm = this.alertCtrl.create({
            title: 'Eliminar paquete',
            message: 'Estás a punto de eliminar el paquete seleccionado, ¿deseas continuar?',
            buttons: [
                {
                    text: 'Cancelar',
                    handler: function () {
                        _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg);
                    }
                },
                {
                    text: 'Aceptar',
                    handler: function () {
                        _this.remove_pkg(package_id);
                    }
                }
            ]
        });
        confirm.present();
    };
    StockMoveListPage.prototype.ngOnDestroy = function () {
        this.subs.unsubscribe();
    };
    StockMoveListPage.prototype.ionViewDidLoad = function () {
        console.log('ionViewDidLoad StockMoveListPage');
    };
    StockMoveListPage.prototype.get_selected_warehouse = function () {
        var _this = this;
        this.storage.get('wh_output_stock_loc_id').then(function (val) {
            _this.default_warehouse = val;
            _this.get_users_list_apk();
            /* this.get_users_list() */
        });
    };
    StockMoveListPage.prototype.get_owner_id = function () {
        var _this = this;
        this.storage.get('USER').then(function (val) {
            _this.owner_id = val;
            _this.get_selected_warehouse();
        });
    };
    StockMoveListPage.prototype.get_users_list_apk = function () {
        var _this = this;
        this.stockInfo.get_users_list_for_apk(this.default_warehouse).then(function (lines) {
            _this.users_list = lines;
            if (_this.passed_selected_partner) {
                _this.get_partner_move_lines_apk(_this.passed_selected_partner, _this.passed_selected_pkg);
                if (_this.passed_shipping_type) {
                    _this.current_shipping_type = _this.passed_shipping_type;
                }
            }
            _this.changeDetectorRef.detectChanges();
            _this.full_users_list = lines;
            return _this.users_list;
        });
    };
    StockMoveListPage.prototype.filter_users_list = function (ev) {
        this.users_list = this.full_users_list;
        var val = ev.target.value;
        if (val && val.trim() != '') {
            this.users_list = this.users_list.filter(function (user) {
                return (user[1].toLowerCase().indexOf(val.toLowerCase()) > -1);
            });
        }
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.get_user_name = function (partner_id) {
        var selected_partner = this.users_list.filter(function (x) { return x[0] == partner_id; });
        this.selected_partner_name = selected_partner[0][1];
        this.selected_partner_default_shipping_type = selected_partner[0][2];
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.get_partner_move_lines_apk = function (partner_id, current_selected_pkg) {
        var _this = this;
        if (current_selected_pkg === void 0) { current_selected_pkg = false; }
        this.current_selected_partner = partner_id;
        this.current_selected_pkg = current_selected_pkg;
        this.get_user_name(this.current_selected_partner);
        this.show_shipping_type(this.selected_partner_default_shipping_type);
        this.stockInfo.get_stock_move_lines_list_apk(partner_id, this.default_warehouse).then(function (lines) {
            _this.full_stock_moves = [];
            _this.filtered_arrival_pkg_list = [];
            _this.current_partner_pkg_list = [];
            _this.current_partner_arrival_pkgs_list = [];
            _this.selected_pkg_default_shipping = false;
            _this.selected_pkg_selected_shipping = false;
            _this.selected_pkg_delivery_carrier_id = false;
            _this.selected_pkg_selected_route_id = false;
            _this.selected_pkg_current_shipping_type = false;
            _this.filtered_pkg_list = [];
            _this.current_partner_pkg_list = lines['result_package_ids'];
            _this.full_stock_moves = lines['move_lines'];
            _this.current_partner_arrival_pkgs_list = lines['arrival_package_ids'];
            _this.get_partner_empty_packages(partner_id);
        }).catch(function (mierror) {
            _this.full_stock_moves = [];
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
        this.current_list_shown = 'move_list';
        if (this.current_selected_pkg != false) {
            this.open_package(this.current_selected_pkg);
        }
    };
    StockMoveListPage.prototype.show_partner_move_lines = function () {
        this.current_list_shown = 'move_list';
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.show_partner_packages_arrivals = function () {
        this.current_list_shown = 'package_list';
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.show_shipping_type = function (shipping_type, front) {
        if (front === void 0) { front = false; }
        this.current_shipping_type = shipping_type;
        if (front == true) {
            this.current_selected_pkg = false;
        }
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.moves_filter_by_assigned_pkgs = function (value) {
        if (value == 0) {
            this.current_list_shown = 'filtered_unassigned';
        }
        else {
            this.current_list_shown = 'filtered_assigned';
        }
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.create_new_package = function (move_id, shipping_type) {
        var _this = this;
        if (shipping_type === void 0) { shipping_type = this.current_shipping_type; }
        this.stockInfo.create_new_package('stock.quant.package', this.current_selected_partner, shipping_type).then(function (linea) {
            _this.stockInfo.add_package_id_to_line(move_id, linea).then(function (resultado) {
                _this.current_selected_pkg = linea;
                _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, _this.current_shipping_type);
            }).catch(function (mierror) {
                _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
            });
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    StockMoveListPage.prototype.create_new_package_for_partner = function (shipping_type) {
        var _this = this;
        if (shipping_type === void 0) { shipping_type = this.current_shipping_type; }
        this.stockInfo.create_new_package('stock.quant.package', this.current_selected_partner, shipping_type).then(function (linea) {
            _this.current_selected_pkg = linea;
            _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, _this.current_shipping_type);
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    StockMoveListPage.prototype.add_product_to_package = function (move_id, reload) {
        var _this = this;
        if (reload === void 0) { reload = true; }
        this.stockInfo.add_package_id_to_line(move_id, this.current_selected_pkg, this.current_shipping_type).then(function (resultado) {
            if (reload == true) {
                _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, _this.current_shipping_type);
            }
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    StockMoveListPage.prototype.add_package_content_to_package = function (package_id) {
        var _this = this;
        var arrival_package_moves = this.full_stock_moves;
        if (package_id) {
            arrival_package_moves = arrival_package_moves.filter(function (x) { return x['package_id'][0] == package_id; });
        }
        arrival_package_moves.forEach(function (package_move) {
            _this.add_product_to_package(package_move['id'], false);
        });
        this.reload_with_data(this.current_selected_partner, this.current_selected_pkg, this.current_shipping_type);
    };
    StockMoveListPage.prototype.open_package = function (package_id) {
        var _this = this;
        this.current_selected_pkg = package_id;
        this.changeDetectorRef.detectChanges();
        this.stockInfo.get_package_lines(package_id).then(function (lineas) {
            _this.current_pkg_info = lineas;
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
        this.stockInfo.get_package_info(package_id).then(function (lineas) {
            var current_shipping_selection = lineas[0]['shipping_type'] || lineas[0]['partner_default_shipping_type'];
            if (current_shipping_selection == 'pasaran') {
                _this.selected_pkg_current_shipping_type = "Pasarán";
            }
            else if (current_shipping_selection == 'agency') {
                _this.selected_pkg_current_shipping_type = lineas[0]['delivery_carrier_id'][1];
            }
            else if (current_shipping_selection == 'route') {
                _this.selected_pkg_current_shipping_type = lineas[0]['selected_route'][1];
            }
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
        this.changeDetectorRef.detectChanges();
    };
    // Shipping type
    StockMoveListPage.prototype.show_shipping_options = function (package_id) {
        var _this = this;
        this.stockInfo.get_package_info(package_id).then(function (lineas) {
            _this.selected_pkg_default_shipping = lineas[0]['partner_default_shipping_type'];
            _this.selected_pkg_selected_shipping = lineas[0]['shipping_type'];
            _this.selected_pkg_delivery_carrier_id = lineas[0]['delivery_carrier_id'];
            _this.selected_pkg_selected_route_id = lineas[0]['selected_route'];
            _this.presentShippingSheet(package_id);
            _this.changeDetectorRef.detectChanges();
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    StockMoveListPage.prototype.show_shipping_options_line = function (line_id) {
        var _this = this;
        this.stockInfo.get_move_line_info(line_id).then(function (linea) {
            _this.selected_line_default_shipping = linea[0]['partner_default_shipping_type'];
            _this.selected_line_selected_shipping = linea[0]['shipping_type'];
            if (!linea[0]['result_package_id']) {
                _this.presentShippingSheet(line_id, 'line');
                _this.changeDetectorRef.detectChanges();
            }
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    StockMoveListPage.prototype.presentShippingSheet = function (package_id, type) {
        if (type === void 0) { type = 'pkg'; }
        var buttons_list_shipping = [];
        var shipping_type = this.create_shipping_type_button(package_id, 'Pasarán', 'pasaran', type);
        buttons_list_shipping.push(shipping_type);
        shipping_type = this.create_shipping_type_button(package_id, 'Agencia', 'agency', type);
        buttons_list_shipping.push(shipping_type);
        shipping_type = this.create_shipping_type_button(package_id, 'Ruta', 'route', type);
        buttons_list_shipping.push(shipping_type);
        var actionSheet = this.actionSheetCtrl.create({
            title: 'Selecciona el método de envío',
            buttons: buttons_list_shipping,
            'cssClass': 'actionSheetContainer'
        });
        this.changeDetectorRef.detectChanges();
        actionSheet.present();
    };
    StockMoveListPage.prototype.create_shipping_type_button = function (package_id, text, role, type) {
        var _this = this;
        var shipping_type_button = {
            'text': text,
            'role': role,
            handler: function () {
                var valores = {
                    'package': package_id,
                    'shipping_type': role
                };
                _this.set_shipping_type(package_id, valores, role, type);
            },
            'cssClass': 'actionSheetButton'
        };
        if (this.selected_pkg_selected_shipping == role || this.selected_line_selected_shipping == role) {
            shipping_type_button['cssClass'] += ' selected';
            shipping_type_button['text'] = shipping_type_button['text'];
        }
        this.changeDetectorRef.detectChanges();
        return shipping_type_button;
    };
    StockMoveListPage.prototype.set_shipping_type = function (package_id, valores, role, type) {
        var _this = this;
        if (type == 'pkg') {
            this.stockInfo.set_package_shipping_type(valores).then(function (resultado) {
                if (role == 'pasaran') {
                    _this.reload_with_data(_this.current_selected_partner, package_id, role);
                }
                else if (role == 'agency') {
                    _this.reload_with_data(_this.current_selected_partner, package_id, role);
                    //this.show_delivery_carriers(package_id)
                }
                else if (role == 'route') {
                    _this.reload_with_data(_this.current_selected_partner, package_id, role);
                    //this.show_route_options(package_id)
                }
                _this.changeDetectorRef.detectChanges();
            }).catch(function (mierror) {
                _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
            });
        }
        else if (type == 'line') {
            this.stockInfo.set_move_line_info(package_id, valores).then(function (resultado) {
                _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, role);
                _this.changeDetectorRef.detectChanges();
            }).catch(function (mierror) {
                _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
            });
        }
    };
    // Routes
    StockMoveListPage.prototype.show_route_options = function (package_id) {
        var _this = this;
        var domain = [['active', '=', true], ['warehouse_selectable', '=', true], ['company_id', '=', this.default_warehouse]];
        this.stockInfo.get_routes(domain).then(function (lineas) {
            _this.presentRoutesSheet(package_id, lineas);
            _this.changeDetectorRef.detectChanges();
        });
    };
    StockMoveListPage.prototype.presentRoutesSheet = function (package_id, routes) {
        var _this = this;
        var buttons_list_routes = [];
        routes.forEach(function (route) {
            var route_button = {
                'text': route['name'],
                'role': route['id'],
                handler: function () {
                    var valores = {
                        'selected_route': route['id']
                    };
                    _this.set_shipping_route(package_id, valores);
                },
                'cssClass': 'actionSheetButton'
            };
            if (_this.selected_pkg_selected_route_id[0] == route['id']) {
                route_button['cssClass'] += ' selected';
                route_button['text'] = '[x]' + route_button['text'];
            }
            buttons_list_routes.push(route_button);
        });
        var actionSheet = this.actionSheetCtrl.create({
            title: 'Selecciona el método de envío',
            buttons: buttons_list_routes,
            'cssClass': 'actionSheetContainer'
        });
        this.changeDetectorRef.detectChanges();
        actionSheet.present();
    };
    StockMoveListPage.prototype.set_shipping_route = function (package_id, valores) {
        var _this = this;
        this.stockInfo.set_package_info(package_id, valores).then(function (resultado) {
            _this.reload_with_data(_this.current_selected_partner, package_id);
            _this.changeDetectorRef.detectChanges();
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    // Delivery carriers
    StockMoveListPage.prototype.show_delivery_carriers = function (package_id) {
        var _this = this;
        var domain = [['active', '=', true], ['company_id', '=', this.default_warehouse]];
        this.stockInfo.get_delivery_carriers(domain).then(function (lineas) {
            _this.presentActionSheet(package_id, lineas);
            _this.changeDetectorRef.detectChanges();
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    StockMoveListPage.prototype.presentActionSheet = function (package_id, delivery_carriers) {
        var _this = this;
        var buttons_list = [];
        delivery_carriers.forEach(function (carrier) {
            var carrier_button = {
                'text': carrier['name'],
                'role': carrier['id'],
                handler: function () {
                    var valores = {
                        'delivery_carrier_id': carrier['id']
                    };
                    _this.set_delivery_carrier(package_id, valores);
                },
                'cssClass': 'actionSheetButton'
            };
            if (_this.selected_pkg_delivery_carrier_id[0] == carrier['id']) {
                carrier_button['cssClass'] += ' selected';
                carrier_button['text'] = '[x]' + carrier_button['text'];
            }
            buttons_list.push(carrier_button);
        });
        var actionSheet = this.actionSheetCtrl.create({
            title: 'Selecciona el método de envío',
            buttons: buttons_list,
            'cssClass': 'actionSheetContainer'
        });
        this.changeDetectorRef.detectChanges();
        actionSheet.present();
    };
    StockMoveListPage.prototype.set_delivery_carrier = function (package_id, valores) {
        var _this = this;
        this.stockInfo.set_package_info(package_id, valores).then(function (resultado) {
            _this.reload_with_data(_this.current_selected_partner, package_id);
            _this.changeDetectorRef.detectChanges();
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    // Package
    StockMoveListPage.prototype.remove_pkg = function (pkg_id) {
        var _this = this;
        this.stockInfo.delete_package(pkg_id).then(function (resultado) {
            _this.reload_with_data(_this.current_selected_partner, false, _this.current_shipping_type);
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    StockMoveListPage.prototype.remove_product_from_pkg = function (move_id) {
        var _this = this;
        this.stockInfo.add_package_id_to_line(move_id, null).then(function (resultado) {
            _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, _this.current_shipping_type);
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    StockMoveListPage.prototype.get_partner_empty_packages = function (partner_id) {
        var _this = this;
        this.stockInfo.get_partner_empty_packages(partner_id).then(function (resultado) {
            resultado.forEach(function (linea) {
                _this.current_partner_pkg_list.push(linea);
                _this.changeDetectorRef.detectChanges();
            });
        }).catch(function (mierror) {
            _this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros');
        });
    };
    // Reload
    StockMoveListPage.prototype.reload_with_data = function (current_selected_partner, current_selected_pkg, current_shipping_type) {
        if (current_selected_pkg === void 0) { current_selected_pkg = false; }
        if (current_shipping_type === void 0) { current_shipping_type = false; }
        var val = { 'current_selected_partner': current_selected_partner, 'current_selected_pkg': current_selected_pkg, 'current_shipping_type': current_shipping_type };
        this.navCtrl.setRoot(StockMoveListPage_1, val);
    };
    StockMoveListPage = StockMoveListPage_1 = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["m" /* Component */])({
            selector: 'stock-move-list',template:/*ion-inline-start:"/home/kiko/ionic/packing_apk/src/pages/stock-move-list/stock-move-list.html"*/'<!--\n  Generated template for the PickingListPage page.\n\n  See http://ionicframework.com/docs/components/#navigation for more info on\n  Ionic pages and navigation.\n-->\n<ion-header>\n  <ion-navbar>\n    <button ion-button menuToggle>\n      <ion-icon name="menu"></ion-icon>\n    </button>\n    <ion-title *ngIf="current_selected_partner && selected_partner_name">Movimientos de stock: {{ selected_partner_name }}\n    </ion-title>\n    <ion-title *ngIf="!current_selected_partner || !selected_partner_name">Movimientos de stock</ion-title>\n\n    <ion-buttons end>\n\n      <button tooltip="Pasarán" positionV="bottom" ion-button icon-only item-end [ngClass]="{\'red-icon\': current_shipping_type == \'pasaran\'}" (click)="show_shipping_type(\'pasaran\', true)" outline icon-only>\n        <ion-icon name="hand" is-active="true"></ion-icon>\n      </button>\n        \n      <button tooltip="Agencia" positionV="bottom" ion-button icon-only item-end [ngClass]="{\'red-icon\': current_shipping_type == \'agency\'}" (click)="show_shipping_type(\'agency\', true)" outline icon-only>\n        <ion-icon name="home" is-active="true"></ion-icon>\n      </button>\n\n      <button tooltip="Ruta" positionV="bottom" ion-button icon-only item-end [ngClass]="{\'red-icon\': current_shipping_type == \'route\'}" (click)="show_shipping_type(\'route\', true)" outline icon-only>\n        <ion-icon name="compass" is-active="true"></ion-icon>\n      </button>\n    </ion-buttons>\n\n  </ion-navbar> \n</ion-header>\n\n<ion-content padding>\n  <ion-grid>\n    <ion-row>\n      <ion-col col-2 col-xs-12 col-sm-12 col-md-6 col-lg-2 col-xl-2>\n        <ion-row>\n          <ion-grid>\n            <ion-scroll id="users" scrollY=true>\n              <ion-row class="row header">\n                <ion-col col-12 class="col">\n                    Clientes\n                </ion-col>\n              </ion-row>\n              <ion-row class="row">\n                <ion-col col-12 class="col">\n                  <ion-searchbar (ionInput)="filter_users_list($event)"></ion-searchbar>\n                </ion-col>\n              </ion-row>\n              <ion-row class="row" *ngFor="let user of users_list">\n                <ion-col col-12 class="col fat-col" [ngClass]="{\'red-background\': user[0] == current_selected_partner}" (click)= "get_partner_move_lines_apk(user[0])">\n                    {{ user[1] }}\n                </ion-col>\n              </ion-row>\n            </ion-scroll>\n          </ion-grid>\n        </ion-row>\n      </ion-col>\n      <ion-col col-6 col-xs-12 col-sm-12 col-md-6 col-lg-6 col-xl-6>\n        <ion-grid>\n          <ion-scroll scrollY=true>\n            <ion-row class="row header filter" *ngIf="current_selected_partner && selected_partner_name">\n              <ion-col col-3>\n                <button color="default" tooltip="Movimientos" positionV="top" arrow [ngClass]="{\'red-icon\': current_list_shown == \'move_list\'}" (click)="show_partner_move_lines()" outline icon-only>\n                  <ion-icon name=\'clipboard\' is-active="true"></ion-icon>\n                </button>\n              </ion-col>\n              <ion-col col-3>\n                <button color="default" tooltip="Paquetes Entrantes" positionV="top" arrow [ngClass]="{\'red-icon\': current_list_shown == \'package_list\'}" (click)="show_partner_packages_arrivals()" outline icon-only>\n                  <ion-icon name=\'cube\' is-active="true"></ion-icon>\n                </button>\n              </ion-col>\n              <ion-col col-3>\n                <button color="default" tooltip="Movimientos sin asignar" positionV="top" arrow *ngIf="current_list_shown == \'move_list\'  || current_list_shown == \'filtered_assigned\'  || current_list_shown == \'filtered_unassigned\'" [ngClass]="{\'red-icon\': current_list_shown == \'filtered_unassigned\'}" (click)="moves_filter_by_assigned_pkgs(0)" outline icon-only>\n                  <ion-icon name=\'log-in\' is-active="true"></ion-icon>\n                </button>\n              </ion-col>\n              <ion-col col-3>\n                <button color="default" tooltip="Movimientos asignados" positionV="top" arrow *ngIf="current_list_shown == \'move_list\'  || current_list_shown == \'filtered_assigned\'  || current_list_shown == \'filtered_unassigned\'" [ngClass]="{\'red-icon\': current_list_shown == \'filtered_assigned\'}" (click)="moves_filter_by_assigned_pkgs(1)" outline icon-only>\n                  <ion-icon name=\'log-out\' is-active="true"></ion-icon>\n                </button>\n              </ion-col>\n            </ion-row>\n            <div *ngIf="current_list_shown == \'move_list\'  || current_list_shown == \'filtered_assigned\'  || current_list_shown == \'filtered_unassigned\'">\n              <ion-row class="row header">\n                <ion-col col-1 class="col">ID</ion-col>\n                <ion-col col-2 class="col">Pedido</ion-col>\n                <ion-col col-1 class="col">UDs.</ion-col>\n                <ion-col col-3 class="col">P.Entrada</ion-col>\n                <ion-col col-3 class="col">P.Salida</ion-col>\n                <ion-col col-2 class="col">Opc.</ion-col>\n              </ion-row>\n              <div dragula="move_lines_container" id="lines" [dragulaModel]="users_list">\n                <div *ngFor="let move of full_stock_moves" id="{{move[\'id\']}}" (press)="show_shipping_options_line(move[\'id\'])">\n                    <ion-row class="row" *ngIf="((!move[\'shipping_type\'] && move[\'partner_default_shipping_type\'] == current_shipping_type) || (move[\'shipping_type\'] && move[\'shipping_type\'] == current_shipping_type)) && ((current_list_shown == \'filtered_unassigned\' && !move[\'result_package_id\']) || (current_list_shown == \'filtered_assigned\' && move[\'result_package_id\']) || (current_list_shown == \'move_list\'))">\n                      <ion-col col-1 class="col product-col">{{move[\'id\']}}</ion-col>\n                      <ion-col col-2 class="col product-col">{{move[\'origin\']}}</ion-col>\n                      <ion-col col-1 class="col product-col">{{move[\'product_qty\']}}</ion-col>\n                      <ion-col col-3 class="col product-col">{{move[\'package_id\'][1] || \'N\'}}</ion-col>\n                      <ion-col col-3 class="col product-col">{{move[\'result_package_id\'][1] || \'N\'}}</ion-col>\n                      <ion-col col-2 class="col product-col options">\n                        <!-- <div *ngIf="!move[\'result_package_id\']">\n                          <button *ngIf="!current_selected_pkg" color="default" (click)="create_new_package(move[\'id\'])" outline icon-only>\n                            <ion-icon name=\'add-circle\' is-active="true"></ion-icon>\n                          </button>\n                          <button *ngIf="current_selected_pkg" color="default" (click)="add_product_to_package(move[\'id\'])" outline icon-only>\n                            <ion-icon name=\'add-circle\' is-active="true"></ion-icon>\n                          </button>\n                        </div> -->\n                        <div *ngIf="move[\'result_package_id\']">\n                          <button tooltip="Ver" positionV="top" arrow (click)= "open_package(move[\'result_package_id\'][0])" [ngClass]="{\'red-icon\': move[\'result_package_id\'][0] == current_selected_pkg}" color="default" outline icon-only>\n                            <ion-icon name=\'eye\' is-active="true"></ion-icon>\n                          </button>\n                        </div>\n                      </ion-col>\n                      <ion-col col-12 class="col product-col"><strong>{{move[\'name\']}}</strong></ion-col>\n                    </ion-row>\n                  </div>\n              </div>\n            </div>\n            <div *ngIf="current_list_shown == \'package_list\'">\n              <ion-row class="row header">\n                <ion-col col-6 class="col">ID</ion-col>\n                <ion-col col-6 class="col">Nombre</ion-col>\n              </ion-row>\n              <div dragula="move_lines_container" id="arrival_pkgs" [dragulaModel]="current_partner_arrival_pkgs_list">\n                <ion-row class="row" *ngFor="let arrival_pkg of current_partner_arrival_pkgs_list" id="{{arrival_pkg[0]}}">\n                  <ion-col col-6 class="col product-col">{{arrival_pkg[0]}}</ion-col>\n                  <ion-col col-6 class="col product-col">{{arrival_pkg[1]}}</ion-col>\n                </ion-row>\n              </div>\n            </div>\n          </ion-scroll>\n        </ion-grid>\n      </ion-col>\n\n      <ion-col col-4 col-xs-12 col-sm-12 col-md-6 col-lg-4 col-xl-4>\n        <ion-row>\n          <ion-grid>\n            <ion-scroll scrollY=true>\n              <div *ngIf="current_selected_pkg == false">\n                <ion-row class="row header-reddish">\n                  <ion-col col-8 class="col pkg">\n                    Paquetes\n                  </ion-col>\n                  <ion-col col-4 class="col add">\n                    <ion-row>\n                      <ion-col class="col add" col-12>\n                        <button tooltip="Nuevo Paquete" positionV="top" arrow *ngIf="current_selected_partner && selected_partner_name" class="black" icon-only (click)="create_new_package_for_partner()">\n                          <ion-icon name="add-circle"></ion-icon>\n                        </button>\n                      </ion-col>\n                    </ion-row>\n                  </ion-col>\n                </ion-row>\n                <ion-row class="row" dragula="move_lines_container" id="pkgs" [dragulaModel]="current_partner_pkg_list">\n                  <ion-col col-4 class="col fat-col" *ngFor="let pkg of current_partner_pkg_list" id="{{pkg[0]}}" [ngClass]="{\'red-background\': pkg[0] == current_selected_pkg, \'hidden-col\': ((!pkg[2] && pkg[3] != current_shipping_type) || (pkg[2] && pkg[2] != current_shipping_type))}" (click)="open_package(pkg[0])" (press)="show_shipping_options(pkg[0])">\n                    <ion-row>{{pkg[1]}}</ion-row>\n                  </ion-col>\n                </ion-row>\n              </div>\n              <div *ngIf="current_selected_pkg != false">\n                <ion-row class="row header-reddish">\n                  <ion-col col-8 class="col pkg">\n                    Paquetes\n                  </ion-col>\n                  <ion-col col-4 class="col add">\n                    <ion-row>\n                      <ion-col class="col add" col-12>\n                        <button *ngIf="current_selected_partner && selected_partner_name && current_selected_pkg" class="black" icon-only (click)="showDestroyConfirmation(current_selected_pkg)">\n                          <ion-icon name="remove-circle"></ion-icon>\n                        </button>\n                      </ion-col>\n                    </ion-row>\n                  </ion-col>\n                </ion-row>\n                <ion-row class="row header">\n                  <ion-col col-6 class="col pkg">\n                    Contenido del paquete\n                  </ion-col>\n                  <ion-col col-6 class="col add">\n                    <span *ngIf="current_selected_partner && selected_partner_name && current_selected_pkg">Envío: {{ selected_pkg_current_shipping_type }}</span>\n                  </ion-col>\n                </ion-row>\n                <ion-row class="row header">\n                  <ion-col col-6 class="col">Nombre</ion-col>\n                  <ion-col col-6 class="col">Cant.</ion-col>\n                </ion-row>\n                <ion-row>\n                  <ion-col col-12 class="col">\n                    <ion-row class="row" (click)="reload_with_data(current_selected_partner, false, current_shipping_type)">\n                      <ion-icon name="undo"></ion-icon>\n                    </ion-row>\n                  </ion-col>\n                </ion-row>\n                <div dragula="move_lines_container" id="pkgs_info" [dragulaModel]="current_pkg_info">\n                  <ion-row class="row" id="{{pkg_line[0]}}" *ngFor="let pkg_line of current_pkg_info">\n                    <ion-col col-6 class="col product-col">\n                      <ion-row>{{pkg_line[1]}}</ion-row>\n                    </ion-col>\n                    <ion-col col-6 class="col product-col">\n                      <ion-row>{{pkg_line[2]}}</ion-row>\n                    </ion-col>\n                  </ion-row>\n                </div>\n              </div>\n            </ion-scroll>\n          </ion-grid>\n        </ion-row>\n      </ion-col>\n    </ion-row>\n  </ion-grid>\n</ion-content>'/*ion-inline-end:"/home/kiko/ionic/packing_apk/src/pages/stock-move-list/stock-move-list.html"*/,
        }),
        __metadata("design:paramtypes", [__WEBPACK_IMPORTED_MODULE_1_ionic_angular__["b" /* AlertController */], __WEBPACK_IMPORTED_MODULE_1_ionic_angular__["a" /* ActionSheetController */], __WEBPACK_IMPORTED_MODULE_5_ng2_dragula__["b" /* DragulaService */],
            __WEBPACK_IMPORTED_MODULE_1_ionic_angular__["g" /* NavController */], __WEBPACK_IMPORTED_MODULE_1_ionic_angular__["h" /* NavParams */], __WEBPACK_IMPORTED_MODULE_1_ionic_angular__["j" /* ViewController */], __WEBPACK_IMPORTED_MODULE_3__ionic_storage__["b" /* Storage */],
            __WEBPACK_IMPORTED_MODULE_2__providers_stock_stock__["a" /* StockProvider */], __WEBPACK_IMPORTED_MODULE_0__angular_core__["j" /* ChangeDetectorRef */]])
    ], StockMoveListPage);
    return StockMoveListPage;
    var StockMoveListPage_1;
}());

//# sourceMappingURL=stock-move-list.js.map

/***/ }),

/***/ 183:
/***/ (function(module, exports) {

function webpackEmptyAsyncContext(req) {
	// Here Promise.resolve().then() is used instead of new Promise() to prevent
	// uncatched exception popping up in devtools
	return Promise.resolve().then(function() {
		throw new Error("Cannot find module '" + req + "'.");
	});
}
webpackEmptyAsyncContext.keys = function() { return []; };
webpackEmptyAsyncContext.resolve = webpackEmptyAsyncContext;
module.exports = webpackEmptyAsyncContext;
webpackEmptyAsyncContext.id = 183;

/***/ }),

/***/ 225:
/***/ (function(module, exports, __webpack_require__) {

var map = {
	"../pages/stock-move-list/stock-move-list.module": [
		451,
		0
	]
};
function webpackAsyncContext(req) {
	var ids = map[req];
	if(!ids)
		return Promise.reject(new Error("Cannot find module '" + req + "'."));
	return __webpack_require__.e(ids[1]).then(function() {
		return __webpack_require__(ids[0]);
	});
};
webpackAsyncContext.keys = function webpackAsyncContextKeys() {
	return Object.keys(map);
};
webpackAsyncContext.id = 225;
module.exports = webpackAsyncContext;

/***/ }),

/***/ 271:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return TabsPage; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__home_home__ = __webpack_require__(272);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


var TabsPage = /** @class */ (function () {
    function TabsPage() {
        this.tab1Root = __WEBPACK_IMPORTED_MODULE_1__home_home__["a" /* HomePage */];
    }
    TabsPage = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["m" /* Component */])({template:/*ion-inline-start:"/home/kiko/ionic/packing_apk/src/pages/tabs/tabs.html"*/'<ion-tabs>\n  <ion-tab [root]="tab1Root" tabTitle="Inicio" tabIcon="home"></ion-tab>\n</ion-tabs>\n'/*ion-inline-end:"/home/kiko/ionic/packing_apk/src/pages/tabs/tabs.html"*/
        }),
        __metadata("design:paramtypes", [])
    ], TabsPage);
    return TabsPage;
}());

//# sourceMappingURL=tabs.js.map

/***/ }),

/***/ 272:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return HomePage; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_ionic_angular__ = __webpack_require__(40);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__ionic_storage__ = __webpack_require__(65);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__stock_move_list_stock_move_list__ = __webpack_require__(149);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__providers_odoo_odoo__ = __webpack_require__(124);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__providers_stock_stock__ = __webpack_require__(123);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};






var HomePage = /** @class */ (function () {
    function HomePage(navCtrl, navParams, storage, alertCtrl, odoo, stockInfo) {
        this.navCtrl = navCtrl;
        this.navParams = navParams;
        this.storage = storage;
        this.alertCtrl = alertCtrl;
        this.odoo = odoo;
        this.stockInfo = stockInfo;
        this.loginData = { password: '', username: '' };
        this.CONEXION = {
            url: 'http://localhost',
            port: '8069',
            db: '',
            username: '',
            password: '',
            uid: 0,
            context: {},
            user: {}
        };
        this.CONEXION_local = {
            url: '',
            port: '',
            db: '',
            username: '',
            password: '',
            uid: 0,
            context: {},
            user: {}
        };
        this.cargar = false;
        this.mensaje = '';
        this.available_warehouses = [];
        if (this.navParams.get('login')) {
            this.CONEXION.username = this.navParams.get('login');
        }
        ;
        this.check_storage_conexion(this.navParams.get('borrar'));
        if (this.navParams.get('borrar') == true) {
            this.cargar = false;
        }
        else {
            // Autologin al cargar app
            this.cargar = false;
            this.conectarApp(false);
        }
    }
    HomePage.prototype.check_storage_conexion = function (borrar) {
        var _this = this;
        // Fijamos siempre a false el parámetro borrar para no tener que teclear usuario y contraseña siempre
        borrar = false;
        if (borrar) {
            this.CONEXION = this.CONEXION_local;
        }
        else {
            this.storage.get('CONEXION').then(function (val) {
                if (val && val['username']) {
                    _this.CONEXION = val;
                }
                else {
                    _this.CONEXION = _this.CONEXION_local;
                    _this.storage.set('CONEXION', _this.CONEXION).then(function () {
                    });
                }
            });
        }
    };
    HomePage.prototype.presentAlert = function (titulo, texto) {
        var alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    };
    HomePage.prototype.conectarApp = function (verificar) {
        var _this = this;
        this.cargar = true;
        if (verificar) {
            this.storage.set('CONEXION', this.CONEXION).then(function () {
                _this.check_conexion(_this.CONEXION);
            });
        }
        else {
            this.storage.get('CONEXION').then(function (val) {
                var con;
                if (val == null) {
                    _this.cargar = false;
                    con = _this.CONEXION;
                    if (con.username.length < 3 || con.password.length < 3) {
                        if (verificar) {
                            _this.presentAlert('Alerta!', 'Por favor ingrese usuario y contraseña');
                        }
                        return;
                    }
                }
                else {
                    //si los trae directamente ya fueron verificados
                    con = val;
                    if (con.username.length < 3 || con.password.length < 3) {
                        _this.cargar = false;
                        return;
                    }
                }
                if (con) {
                    _this.storage.set('CONEXION', con).then(function () {
                        _this.check_conexion(con);
                        _this.cargar = false;
                    });
                }
            });
        }
    };
    HomePage.prototype.check_conexion = function (con) {
        var _this = this;
        var model = 'res.users';
        var domain = [['login', '=', con.username]];
        var fields = ['id', 'login', 'image', 'name', 'company_id', 'company_ids'];
        this.odoo.login(con.username, con.password).then(function (uid) {
            _this.odoo.uid = uid;
            _this.odoo.search_read(model, domain, fields).then(function (value) {
                if (value) {
                    _this.storage.set('USER', value).then(function () {
                        _this.cargar = false;
                        if (value[0]['company_ids'].length == 1) {
                            _this.storage.set('selected_warehouse', value[0]['company_id']).then(function () {
                                _this.get_output_location_id(value[0]['company_id']);
                            });
                        }
                        else {
                            _this.get_warehouse_options(value[0]['company_ids']);
                        }
                    });
                }
            })
                .catch(function () {
                _this.cargar = false;
                _this.presentAlert('Error!', 'No se pudo encontrar el usuario:' + con.username);
            });
        })
            .catch(function () {
            _this.cargar = false;
            _this.presentAlert('Error!', 'El usuario o contraseña son incorrectos.');
        });
    };
    HomePage.prototype.get_warehouse_options = function (locations) {
        var _this = this;
        this.stockInfo.get_available_warehouse_info(locations, 'form').then(function (lines) {
            _this.show_warehouse_options(lines);
        })
            .catch(function () {
            _this.cargar = false;
            _this.presentAlert('Error!', 'No se pueden recuperar los almacenes');
        });
    };
    HomePage.prototype.show_warehouse_options = function (lines) {
        var _this = this;
        this.available_warehouses = lines;
        var alert = this.alertCtrl.create();
        alert.setTitle('Selecciona un almacén');
        this.available_warehouses.forEach(function (warehouse) {
            if (warehouse['company_id'][0] == _this.available_warehouses[0]['company_id'][0]) {
                alert.addInput({
                    type: 'radio',
                    label: warehouse['name'],
                    value: warehouse['company_id'][0],
                    checked: true
                });
            }
            else {
                alert.addInput({
                    type: 'radio',
                    label: warehouse['name'],
                    value: warehouse['company_id'][0]
                });
            }
        });
        alert.addButton('Cancel');
        alert.addButton({
            text: 'Ok',
            handler: function (data) {
                _this.testRadioOpen = false;
                _this.testRadioResult = data;
                _this.storage.set('selected_warehouse', data).then(function () {
                    _this.get_output_location_id(data);
                });
            }
        });
        alert.present();
    };
    HomePage.prototype.get_output_location_id = function (company_id) {
        var _this = this;
        var model = 'stock.warehouse';
        var domain = [['company_id', '=', company_id], ['active', '=', true]];
        var fields = ['wh_output_stock_loc_id'];
        this.odoo.search_read(model, domain, fields).then(function (result) {
            _this.storage.set('wh_output_stock_loc_id', result[0]['wh_output_stock_loc_id'][0]).then(function () {
                _this.navCtrl.setRoot(__WEBPACK_IMPORTED_MODULE_3__stock_move_list_stock_move_list__["a" /* StockMoveListPage */]);
            });
        }).catch(function () {
            _this.cargar = false;
            _this.presentAlert('Error!', 'No se pueden recuperar los almacenes');
        });
    };
    HomePage = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_1__angular_core__["m" /* Component */])({
            selector: 'page-home',template:/*ion-inline-start:"/home/kiko/ionic/packing_apk/src/pages/home/home.html"*/'<ion-content>\n  <form (ngSubmit)="this.conectarApp(true)">\n    <ion-grid text-center>\n      <ion-row>\n        <ion-col width-100>\n          <div style="text-align: center">\n            <img style="height: 100px" src="assets/imgs/logo.png" alt="App Almacén" />\n          </div>\n        </ion-col>\n      </ion-row>\n      <ion-row>\n        <ion-col width-100>\n        \n        <ion-list *ngIf="!cargar">\n          <ion-item>\n            <ion-label color="primary" stacked>\n              <span class="custom-font-size">Usuario</span>\n            </ion-label>\n            <ion-input type="email" [(ngModel)]="CONEXION.username" required name=\'username\' placeholder="Ingresa Usuario"></ion-input>\n          </ion-item>\n\n          <ion-item>\n            <ion-label color="primary" stacked>\n              <span class="custom-font-size">Contraseña</span>\n            </ion-label>\n            <ion-input type="password" [(ngModel)]="CONEXION.password" required name=\'password\' placeholder="Ingresa Contraseña"></ion-input>\n          </ion-item>\n\n        </ion-list>\n        </ion-col>\n      </ion-row>\n      <ion-row>\n        <ion-col width-100>\n          <button ion-button full type="submit">\n            <span class="custom-font-size">Login</span>\n          </button>\n\n        </ion-col>\n      </ion-row>\n      <ion-row>\n          <ion-col width-100>\n            <ion-item>\n                <ion-label color="dark">Servidor</ion-label>\n                <ion-toggle [(ngModel)]="login_server" [ngModelOptions] = {standalone:true} ></ion-toggle>\n            </ion-item>     \n          </ion-col>\n        </ion-row>\n      <ion-row>\n        <ion-col width-100>\n          <ion-list *ngIf="!cargar && login_server" >\n            <ion-item>\n              <ion-label color="primary" stacked>\n                <span class="custom-font-size">URL</span>\n              </ion-label>\n              <ion-input [(ngModel)]="CONEXION.url" required name=\'url\' placeholder="Ingresa url"></ion-input>\n            </ion-item>\n            <ion-item>\n              <ion-label color="primary" stacked>\n                <span class="custom-font-size">Port</span>\n              </ion-label>\n              <ion-input type="number" [(ngModel)]="CONEXION.port" required name=\'port\' placeholder="Ingresa puerto"></ion-input>\n            </ion-item>\n            <ion-item>\n              <ion-label color="primary" stacked>\n                <span class="custom-font-size">Base de datos</span>\n              </ion-label>\n              <ion-input [(ngModel)]="CONEXION.db" required name=\'db\' placeholder="Ingresa base de datos"></ion-input>\n            </ion-item>\n          </ion-list>\n        </ion-col>\n      </ion-row>\n    </ion-grid>\n\n  </form>\n\n  <div *ngIf="cargar" style="text-align: center">\n    <ion-spinner name="circles"></ion-spinner>\n    <br>\n    <b>Verificando...</b>\n  </div>\n</ion-content>\n'/*ion-inline-end:"/home/kiko/ionic/packing_apk/src/pages/home/home.html"*/
        }),
        __metadata("design:paramtypes", [__WEBPACK_IMPORTED_MODULE_0_ionic_angular__["g" /* NavController */], __WEBPACK_IMPORTED_MODULE_0_ionic_angular__["h" /* NavParams */],
            __WEBPACK_IMPORTED_MODULE_2__ionic_storage__["b" /* Storage */], __WEBPACK_IMPORTED_MODULE_0_ionic_angular__["b" /* AlertController */],
            __WEBPACK_IMPORTED_MODULE_4__providers_odoo_odoo__["a" /* OdooProvider */], __WEBPACK_IMPORTED_MODULE_5__providers_stock_stock__["a" /* StockProvider */]])
    ], HomePage);
    return HomePage;
}());

//# sourceMappingURL=home.js.map

/***/ }),

/***/ 274:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_platform_browser_dynamic__ = __webpack_require__(275);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__app_module__ = __webpack_require__(387);


Object(__WEBPACK_IMPORTED_MODULE_0__angular_platform_browser_dynamic__["a" /* platformBrowserDynamic */])().bootstrapModule(__WEBPACK_IMPORTED_MODULE_1__app_module__["a" /* AppModule */]);
//# sourceMappingURL=main.js.map

/***/ }),

/***/ 387:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return AppModule; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_platform_browser__ = __webpack_require__(42);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_ionic_angular__ = __webpack_require__(40);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__app_component__ = __webpack_require__(437);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__ionic_storage__ = __webpack_require__(65);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_ng2_dragula__ = __webpack_require__(227);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__pages_home_home__ = __webpack_require__(272);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__pages_tabs_tabs__ = __webpack_require__(271);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8__pages_stock_move_list_stock_move_list__ = __webpack_require__(149);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_9__ionic_native_status_bar_ngx__ = __webpack_require__(268);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_10__ionic_native_splash_screen_ngx__ = __webpack_require__(270);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_11__providers_stock_stock__ = __webpack_require__(123);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_12__providers_odoo_odoo__ = __webpack_require__(124);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_13__angular_platform_browser_animations__ = __webpack_require__(447);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_14_ionic_tooltips__ = __webpack_require__(449);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};















var AppModule = /** @class */ (function () {
    function AppModule() {
    }
    AppModule = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["I" /* NgModule */])({
            declarations: [
                __WEBPACK_IMPORTED_MODULE_3__app_component__["a" /* MyApp */],
                __WEBPACK_IMPORTED_MODULE_6__pages_home_home__["a" /* HomePage */],
                __WEBPACK_IMPORTED_MODULE_7__pages_tabs_tabs__["a" /* TabsPage */],
                __WEBPACK_IMPORTED_MODULE_8__pages_stock_move_list_stock_move_list__["a" /* StockMoveListPage */]
            ],
            imports: [
                __WEBPACK_IMPORTED_MODULE_1__angular_platform_browser__["a" /* BrowserModule */],
                __WEBPACK_IMPORTED_MODULE_2_ionic_angular__["e" /* IonicModule */].forRoot(__WEBPACK_IMPORTED_MODULE_3__app_component__["a" /* MyApp */], {}, {
                    links: [
                        { loadChildren: '../pages/stock-move-list/stock-move-list.module#PickingListPageModule', name: 'StockMoveListPage', segment: 'stock-move-list', priority: 'low', defaultHistory: [] }
                    ]
                }),
                __WEBPACK_IMPORTED_MODULE_4__ionic_storage__["a" /* IonicStorageModule */].forRoot(),
                __WEBPACK_IMPORTED_MODULE_5_ng2_dragula__["a" /* DragulaModule */].forRoot(),
                __WEBPACK_IMPORTED_MODULE_13__angular_platform_browser_animations__["a" /* BrowserAnimationsModule */],
                __WEBPACK_IMPORTED_MODULE_14_ionic_tooltips__["a" /* TooltipsModule */].forRoot()
                /* Para Android ~9 hay que poner poner websql para que funcione.
                
                IonicStorageModule.forRoot(
                  {
                    name: '__mydb',
                    driverOrder: ['sqlite', 'websql', 'indexeddb']
                    }
                )
                 Si se activa siempre no funciona en navegadores de incógnito.
                */
            ],
            bootstrap: [__WEBPACK_IMPORTED_MODULE_2_ionic_angular__["c" /* IonicApp */]],
            entryComponents: [
                __WEBPACK_IMPORTED_MODULE_3__app_component__["a" /* MyApp */],
                __WEBPACK_IMPORTED_MODULE_6__pages_home_home__["a" /* HomePage */],
                __WEBPACK_IMPORTED_MODULE_7__pages_tabs_tabs__["a" /* TabsPage */],
                __WEBPACK_IMPORTED_MODULE_8__pages_stock_move_list_stock_move_list__["a" /* StockMoveListPage */]
            ],
            providers: [
                __WEBPACK_IMPORTED_MODULE_9__ionic_native_status_bar_ngx__["a" /* StatusBar */],
                __WEBPACK_IMPORTED_MODULE_10__ionic_native_splash_screen_ngx__["a" /* SplashScreen */],
                __WEBPACK_IMPORTED_MODULE_11__providers_stock_stock__["a" /* StockProvider */],
                __WEBPACK_IMPORTED_MODULE_12__providers_odoo_odoo__["a" /* OdooProvider */],
                { provide: __WEBPACK_IMPORTED_MODULE_0__angular_core__["u" /* ErrorHandler */], useClass: __WEBPACK_IMPORTED_MODULE_2_ionic_angular__["d" /* IonicErrorHandler */] }
            ]
        })
    ], AppModule);
    return AppModule;
}());

//# sourceMappingURL=app.module.js.map

/***/ }),

/***/ 437:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return MyApp; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_ionic_angular__ = __webpack_require__(40);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__ionic_native_status_bar_ngx__ = __webpack_require__(268);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__ionic_native_splash_screen_ngx__ = __webpack_require__(270);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__pages_tabs_tabs__ = __webpack_require__(271);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};





var MyApp = /** @class */ (function () {
    function MyApp(platform, statusBar, splashScreen) {
        this.rootPage = __WEBPACK_IMPORTED_MODULE_4__pages_tabs_tabs__["a" /* TabsPage */];
        platform.ready().then(function () {
            // Okay, so the platform is ready and our plugins are available.
            // Here you can do any higher level native things you might need.
            statusBar.styleDefault();
            splashScreen.hide();
        });
    }
    MyApp = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["m" /* Component */])({template:/*ion-inline-start:"/home/kiko/ionic/packing_apk/src/app/app.html"*/'<ion-nav [root]="rootPage"></ion-nav>\n'/*ion-inline-end:"/home/kiko/ionic/packing_apk/src/app/app.html"*/
        }),
        __metadata("design:paramtypes", [__WEBPACK_IMPORTED_MODULE_1_ionic_angular__["i" /* Platform */], __WEBPACK_IMPORTED_MODULE_2__ionic_native_status_bar_ngx__["a" /* StatusBar */], __WEBPACK_IMPORTED_MODULE_3__ionic_native_splash_screen_ngx__["a" /* SplashScreen */]])
    ], MyApp);
    return MyApp;
}());

//# sourceMappingURL=app.component.js.map

/***/ })

},[274]);
//# sourceMappingURL=main.js.map