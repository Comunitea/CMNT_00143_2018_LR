webpackJsonp([1],{

/***/ 125:
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
        console.log(values);
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

/***/ 150:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return StockMoveListPage; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_ionic_angular__ = __webpack_require__(41);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__providers_stock_stock__ = __webpack_require__(82);
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
        this.multipleSelectionMain = false;
        this.passed_selected_partner = this.navParams.data.current_selected_partner;
        this.passed_selected_pkg = this.navParams.data.current_selected_pkg;
        this.passed_shipping_type = this.navParams.data.current_shipping_type;
        this.passed_current_list_shown = this.navParams.data.current_list_shown;
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
        this.selected_pkg_selected_shipping = false;
        this.selected_pkg_delivery_carrier_id = false;
        this.selected_pkg_selected_route_id = false;
        this.current_list_shown = false;
        this.selected_partner_default_shipping_type = false;
        this.current_shipping_type = false;
        this.current_partner_arrival_pkgs_list = [];
        this.filtered_arrival_pkg_list = [];
        this.selected_line_selected_shipping = [];
        this.current_pkg_data = [];
        this.packaging_line_ids = [];
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
                _this.update_packages(parseInt(el.id), false, "new");
            }
            else if (target.id == "pkgs_info" && source.id == "lines") {
                _this.update_packages(parseInt(el.id));
            }
            else if (target.id == "pkgs_info" && source.id == "arrival_pkgs") {
                _this.add_package_content_to_package(parseInt(el.id));
            }
        }));
        this.subs.add(this.dragulaService.removeModel()
            .subscribe(function (_a) {
            var el = _a.el, source = _a.source;
            if (source.id == "pkgs_info") {
                _this.update_packages(parseInt(el.id), false, "unlink");
            }
            else if (source.id == "lines" || source.id == "arrival_pkgs") {
                _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg);
            }
        }));
        dragulaService.destroy("move_lines_container");
        dragulaService.createGroup("move_lines_container", {
            removeOnSpill: false,
            revertOnSpill: true,
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
            if (_this.passed_current_list_shown) {
                _this.current_list_shown = _this.passed_current_list_shown;
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
                return (user['name'].toLowerCase().indexOf(val.toLowerCase()) > -1);
            });
        }
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.filter_users_list_from_server = function (ev) {
        var _this = this;
        var val = ev.target.value;
        this.stockInfo.get_users_list_for_apk_from_search_box(val).then(function (lines) {
            _this.users_list = lines;
        }).catch(function (mierror) {
            _this.full_stock_moves = [];
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror + mierror)
            console.log(mierror);
        });
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.get_user_name = function (partner_id) {
        var selected_partner = this.users_list.filter(function (x) { return x['id'] == partner_id; });
        this.selected_partner_name = selected_partner[0]['name'];
        this.selected_partner_default_shipping_type = selected_partner[0]['shipping_type'] || 'pasaran';
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.get_partner_move_lines_apk = function (partner_id, current_selected_pkg) {
        var _this = this;
        if (current_selected_pkg === void 0) { current_selected_pkg = false; }
        this.current_selected_partner = partner_id;
        this.current_selected_pkg = current_selected_pkg;
        this.get_user_name(this.current_selected_partner);
        this.show_shipping_type('all');
        this.stockInfo.get_stock_move_lines_list_apk(partner_id, this.default_warehouse).then(function (lines) {
            console.log(lines);
            _this.multipleSelectionMain = false;
            _this.full_stock_moves = [];
            _this.filtered_arrival_pkg_list = [];
            _this.current_partner_pkg_list = [];
            _this.current_partner_arrival_pkgs_list = [];
            _this.selected_pkg_selected_shipping = false;
            _this.selected_pkg_delivery_carrier_id = false;
            _this.selected_pkg_selected_route_id = false;
            _this.selected_pkg_current_shipping_type = false;
            _this.filtered_pkg_list = [];
            _this.current_partner_pkg_list = lines['result_package_ids'];
            _this.full_stock_moves = lines['move_lines'];
            _this.current_partner_arrival_pkgs_list = lines['arrival_package_ids'];
        }).catch(function (mierror) {
            _this.full_stock_moves = [];
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror + mierror)
            console.log(mierror);
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
    StockMoveListPage.prototype.update_packages = function (move_ids, package_id, action, partner_id) {
        var _this = this;
        if (package_id === void 0) { package_id = this.current_selected_pkg; }
        if (action === void 0) { action = false; }
        if (partner_id === void 0) { partner_id = false; }
        console.log(partner_id);
        this.stockInfo.update_object('stock.move.line', action, move_ids, false, package_id, partner_id).then(function (resultado) {
            if (resultado[0]) {
                _this.current_selected_pkg = resultado[0] || false;
            }
            _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, _this.current_shipping_type);
        }).catch(function (mierror) {
            _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, _this.current_shipping_type);
            console.log(mierror);
        });
    };
    StockMoveListPage.prototype.add_package_content_to_package = function (package_id) {
        var _this = this;
        var action = false;
        if (this.current_selected_pkg == false) {
            action = 'new';
        }
        this.stockInfo.update_object('stock.quant.package', action, [], package_id, this.current_selected_pkg, false).then(function (linea) {
            console.log(linea);
            _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, _this.current_shipping_type);
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
            _this.reload_with_data(_this.current_selected_partner);
            console.log(mierror);
        });
        this.reload_with_data(this.current_selected_partner, this.current_selected_pkg, this.current_shipping_type);
    };
    StockMoveListPage.prototype.open_package = function (package_id) {
        var _this = this;
        this.current_selected_pkg = package_id;
        this.changeDetectorRef.detectChanges();
        this.stockInfo.get_package_lines(package_id).then(function (lineas) {
            _this.current_pkg_info = lineas['move_lines_info'];
            _this.current_pkg_data = lineas['package_info'];
            _this.packaging_line_ids = lineas['packaging_line_info'];
            console.log(lineas['packaging_line_info']);
            console.log(_this.packaging_line_ids);
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
            _this.reload_with_data(_this.current_selected_partner, false, _this.current_shipping_type);
            console.log(mierror);
        });
        this.stockInfo.get_package_info(package_id).then(function (lineas) {
            var current_shipping_selection = lineas[0]['shipping_type'] || lineas[0]['partner_default_shipping_type'];
            if (current_shipping_selection == 'pasaran') {
                _this.selected_pkg_current_shipping_type = "Pasarán";
            }
            else if (current_shipping_selection == 'urgent' && lineas[0]['delivery_carrier_id']) {
                _this.selected_pkg_current_shipping_type = lineas[0]['delivery_carrier_id'][1] || false;
            }
            else if (current_shipping_selection == 'route' && lineas[0]['selected_route']) {
                _this.selected_pkg_current_shipping_type = lineas[0]['selected_route'][1] || false;
            }
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
            _this.reload_with_data(_this.current_selected_partner, false, _this.current_shipping_type);
            console.log(mierror);
        });
        this.changeDetectorRef.detectChanges();
    };
    // Shipping type
    StockMoveListPage.prototype.show_shipping_options = function (package_id) {
        var _this = this;
        this.stockInfo.get_package_info(package_id).then(function (lineas) {
            _this.selected_pkg_selected_shipping = lineas[0]['shipping_type'] || false;
            _this.selected_pkg_delivery_carrier_id = lineas[0]['delivery_carrier_id'] || false;
            _this.selected_pkg_selected_route_id = lineas[0]['selected_route'] || false;
            _this.presentShippingSheet(package_id);
            _this.changeDetectorRef.detectChanges();
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
            _this.reload_with_data(_this.current_selected_partner, false, _this.current_shipping_type);
            console.log(mierror);
        });
    };
    StockMoveListPage.prototype.show_shipping_options_line = function (line_id) {
        var _this = this;
        console.log("linea: " + line_id);
        this.stockInfo.get_move_line_info(line_id).then(function (linea) {
            console.log(linea);
            _this.selected_line_selected_shipping = linea[0]['shipping_type'];
            if (!linea[0]['result_package_id']) {
                _this.presentShippingSheet(line_id, 'line');
                _this.changeDetectorRef.detectChanges();
            }
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
            _this.reload_with_data(_this.current_selected_partner, false, _this.current_shipping_type);
            console.log(mierror);
        });
    };
    StockMoveListPage.prototype.presentShippingSheet = function (package_id, type) {
        if (type === void 0) { type = 'pkg'; }
        var buttons_list_shipping = [];
        var shipping_type = this.create_shipping_type_button(package_id, 'Pasarán', 'pasaran', type);
        buttons_list_shipping.push(shipping_type);
        shipping_type = this.create_shipping_type_button(package_id, 'Urgente', 'urgent', type);
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
        var color = role + '-type';
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
            'cssClass': 'actionSheetButton ' + color
        };
        if (this.selected_pkg_selected_shipping == role || this.selected_line_selected_shipping == role) {
            shipping_type_button['cssClass'] += ' selected';
            shipping_type_button['text'] = shipping_type_button['text'];
        }
        this.changeDetectorRef.detectChanges();
        return shipping_type_button;
    };
    // Package
    StockMoveListPage.prototype.remove_pkg = function (pkg_id) {
        var _this = this;
        this.stockInfo.delete_package(pkg_id).then(function (resultado) {
            _this.reload_with_data(_this.current_selected_partner, false, _this.current_shipping_type);
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
            _this.reload_with_data(_this.current_selected_partner, false, _this.current_shipping_type);
            console.log(mierror);
        });
    };
    // Reload
    StockMoveListPage.prototype.reload_with_data = function (current_selected_partner, current_selected_pkg, current_shipping_type) {
        if (current_selected_pkg === void 0) { current_selected_pkg = false; }
        if (current_shipping_type === void 0) { current_shipping_type = false; }
        var val = { 'current_selected_partner': current_selected_partner, 'current_selected_pkg': current_selected_pkg, 'current_shipping_type': current_shipping_type, 'current_list_shown': this.current_list_shown };
        this.navCtrl.setRoot(StockMoveListPage_1, val);
    };
    // Checkboxes selection
    StockMoveListPage.prototype.multipleSelection = function (event) {
        var checkeableItems = this.full_stock_moves.filter(function (x) { return x; });
        checkeableItems.forEach(function (item) {
            item.isChecked = event.checked;
        });
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.simpleSelection = function (event, id) {
        var item = this.full_stock_moves.filter(function (x) { return x['id'] == id; });
        item.isChecked = event.checked;
        this.changeDetectorRef.detectChanges();
    };
    StockMoveListPage.prototype.add_multiple_lines_to_package = function (type) {
        var _this = this;
        if (type === void 0) { type = 'add'; }
        var selectedItems = this.full_stock_moves.filter(function (x) { return x['isChecked'] == true; });
        var move_line_ids = [];
        selectedItems.forEach(function (item) {
            move_line_ids.push(item.id);
        });
        var action = "notnew";
        if (type == 'add') {
            if (this.current_selected_pkg == false) {
                action = "new";
            }
        }
        else if (type == 'del') {
            this.current_selected_pkg = false;
            action = 'unlink';
        }
        this.stockInfo.update_object('stock.move.line', action, move_line_ids, false, this.current_selected_pkg, false).then(function (linea) {
            _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, _this.current_shipping_type);
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
            _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, _this.current_shipping_type);
            console.log(mierror);
        });
    };
    // Save shipping_type options
    StockMoveListPage.prototype.set_shipping_type = function (id, values, role, type) {
        if (role == 'pasaran') {
            this.update_shipping_type(id, type, values, role);
        }
        else if (role == 'urgent') {
            this.show_delivery_carriers(id, type, values, role);
        }
        else if (role == 'route') {
            this.delivery_or_route_choice_selector(id, type, values, role);
        }
    };
    StockMoveListPage.prototype.update_shipping_type = function (id, type, values, role) {
        var _this = this;
        if (type == 'line') {
            values['move_line'] = id;
            this.stockInfo.set_move_line_shipping_type(values).then(function (resultado) {
                _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, role);
                _this.changeDetectorRef.detectChanges();
            }).catch(function (mierror) {
                //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
                _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg, role);
                console.log(mierror);
            });
        }
        else {
            console.log("valores que envío: " + values);
            this.stockInfo.set_package_shipping_type(values).then(function (resultado) {
                console.log("valores que envío: " + values);
                _this.reload_with_data(_this.current_selected_partner, id, role);
            }).catch(function (mierror) {
                //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
                _this.reload_with_data(_this.current_selected_partner, _this.current_selected_pkg);
                console.log(mierror);
            });
        }
    };
    StockMoveListPage.prototype.delivery_or_route_choice_selector = function (id, type, values, role) {
        var _this = this;
        var buttons_list = [];
        var carriers_button = {
            'text': 'Transportistas',
            'role': 'carriers',
            handler: function () {
                _this.show_delivery_carriers(id, type, values, role);
            },
            'cssClass': 'actionSheetButton'
        };
        var routes_button = {
            'text': 'Rutas',
            'role': 'routes',
            handler: function () {
                _this.show_route_options(id, type, values, role);
            },
            'cssClass': 'actionSheetButton'
        };
        buttons_list.push(carriers_button);
        buttons_list.push(routes_button);
        var actionSheet = this.actionSheetCtrl.create({
            title: 'Selecciona el método de envío',
            buttons: buttons_list,
            'cssClass': 'actionSheetContainer'
        });
        this.changeDetectorRef.detectChanges();
        actionSheet.present();
    };
    StockMoveListPage.prototype.show_delivery_carriers = function (id, type, values, role) {
        var _this = this;
        var domain = [['active', '=', true]];
        this.stockInfo.get_delivery_carriers(domain).then(function (lineas) {
            _this.present_delivery_sheet(id, lineas, type, values, role);
            _this.changeDetectorRef.detectChanges();
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
            _this.reload_with_data(_this.current_selected_partner, id);
            console.log(mierror);
        });
    };
    StockMoveListPage.prototype.present_delivery_sheet = function (id, list, type, values, role) {
        var _this = this;
        var buttons_list = [];
        list.forEach(function (carrier) {
            var carrier_button = {
                'text': carrier['name'],
                'role': carrier['id'],
                handler: function () {
                    values['carrier_id'] = carrier['id'];
                    _this.update_shipping_type(id, type, values, role);
                },
                'cssClass': 'actionSheetButton'
            };
            if (_this.selected_pkg_delivery_carrier_id && _this.selected_pkg_delivery_carrier_id[0] == carrier['id']) {
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
    StockMoveListPage.prototype.show_route_options = function (id, type, values, role) {
        var _this = this;
        this.stockInfo.get_routes_for_apk().then(function (lineas) {
            _this.present_routes_sheet(id, lineas, type, values, role);
            _this.changeDetectorRef.detectChanges();
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror);
            _this.reload_with_data(_this.current_selected_partner, false, _this.current_shipping_type);
            console.log(mierror);
        });
    };
    StockMoveListPage.prototype.present_routes_sheet = function (id, routes, type, values, role) {
        var _this = this;
        var buttons_list_routes = [];
        routes.forEach(function (route) {
            var route_button = {
                'text': route['name'],
                'role': route['id'],
                handler: function () {
                    values['delivery_route_path_id'] = route['id'];
                    _this.update_shipping_type(id, type, values, role);
                },
                'cssClass': 'actionSheetButton'
            };
            if (_this.selected_pkg_selected_route_id && _this.selected_pkg_selected_route_id[0] == route['id']) {
                route_button['cssClass'] += ' selected';
                route_button['text'] = '[x]' + route_button['text'];
            }
            buttons_list_routes.push(route_button);
            _this.changeDetectorRef.detectChanges();
        });
        var actionSheet = this.actionSheetCtrl.create({
            title: 'Selecciona el método de envío',
            buttons: buttons_list_routes,
            'cssClass': 'actionSheetContainer'
        });
        this.changeDetectorRef.detectChanges();
        actionSheet.present();
    };
    StockMoveListPage = StockMoveListPage_1 = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["m" /* Component */])({
            selector: 'stock-move-list',template:/*ion-inline-start:"/home/kiko/ionic/packing_apk/src/pages/stock-move-list/stock-move-list.html"*/'<!--\n  Generated template for the PickingListPage page.\n\n  See http://ionicframework.com/docs/components/#navigation for more info on\n  Ionic pages and navigation.\n-->\n<ion-header>\n  <ion-navbar>\n    <button ion-button menuToggle>\n      <ion-icon name="menu"></ion-icon>\n    </button>\n    <ion-title *ngIf="current_selected_partner && selected_partner_name; else not_selected_partner_name">Movimientos de stock: {{ selected_partner_name }}\n    </ion-title>\n\n    <ion-buttons end>\n\n      <button tooltip="Todos" positionV="bottom" ion-button icon-only item-end [ngClass]="{\'all-type\': current_shipping_type == \'all\'}" (click)="show_shipping_type(\'all\', false)" outline icon-only>\n          <ion-icon name="clipboard" is-active="true"></ion-icon>\n        </button>\n\n      <button tooltip="Pasarán" positionV="bottom" ion-button icon-only item-end [ngClass]="{\'pasaran-type\': current_shipping_type == \'pasaran\'}" (click)="show_shipping_type(\'pasaran\', true)" outline icon-only>\n        <ion-icon name="hand" is-active="true"></ion-icon>\n      </button>\n\n      <button tooltip="Ruta" positionV="bottom" ion-button icon-only item-end [ngClass]="{\'route-type\': current_shipping_type == \'route\'}" (click)="show_shipping_type(\'route\', true)" outline icon-only>\n        <ion-icon name="git-branch" is-active="true"></ion-icon>\n      </button>\n\n      <button tooltip="Urgente" positionV="bottom" ion-button icon-only item-end [ngClass]="{\'urgent-type\': current_shipping_type == \'urgent\'}" (click)="show_shipping_type(\'urgent\', true)" outline icon-only>\n        <ion-icon name="subway" is-active="true"></ion-icon>\n      </button>\n    </ion-buttons>\n\n  </ion-navbar> \n</ion-header>\n\n<ion-content padding>\n  <ion-grid>\n    <ion-row>\n      <ion-col col-12 col-xs-12 col-sm-12 col-md-2 col-lg-2 col-xl-2>\n        <ion-row>\n          <ion-grid>\n            <ion-scroll id="users" scrollY=true>\n              <ion-row class="row header">\n                <ion-col col-12 class="col">\n                    Clientes\n                </ion-col>\n              </ion-row>\n              <ion-row class="row">\n                <ion-col col-12 class="col">\n                  <ion-searchbar (ionInput)="filter_users_list_from_server($event)"></ion-searchbar>\n                </ion-col>\n              </ion-row>\n              <ion-row class="row" *ngFor="let user of users_list">\n                <ion-col col-12 class="col fat-col" [ngClass]="{\'red-background\': user[\'id\'] == current_selected_partner}" (click)= "get_partner_move_lines_apk(user[\'id\'])">\n                    {{ user[\'name\'] }}\n                </ion-col>\n              </ion-row>\n            </ion-scroll>\n          </ion-grid>\n        </ion-row>\n      </ion-col>\n      <ion-col col-12 col-xs-12 col-sm-8 col-md-7 col-lg-6 col-xl-6>\n        <ion-grid>\n          <ion-scroll scrollY=true>\n            <ion-row class="row header filter" *ngIf="current_selected_partner && selected_partner_name">\n              <ion-col col-3>\n                <button color="default" class="button-color-first" tooltip="Movimientos" positionV="top" arrow [ngClass]="{\'active-icon\': current_list_shown == \'move_list\'}" (click)="show_partner_move_lines()" outline icon-only>\n                  <ion-icon name=\'paper\' is-active="true"></ion-icon>\n                </button>\n              </ion-col>\n              <ion-col col-3>\n                <button color="default" class="button-color-first" tooltip="Paquetes Entrantes" positionV="top" arrow [ngClass]="{\'active-icon\': current_list_shown == \'package_list\'}" (click)="show_partner_packages_arrivals()" outline icon-only>\n                  <ion-icon name=\'cube\' is-active="true"></ion-icon>\n                </button>\n              </ion-col>\n              <ion-col col-3>\n                <button color="default" class="button-color-first" tooltip="Movimientos sin asignar" positionV="top" arrow *ngIf="current_list_shown == \'move_list\'  || current_list_shown == \'filtered_assigned\'  || current_list_shown == \'filtered_unassigned\'" [ngClass]="{\'active-icon\': current_list_shown == \'filtered_unassigned\'}" (click)="moves_filter_by_assigned_pkgs(0)" outline icon-only>\n                  <ion-icon name=\'log-in\' is-active="true"></ion-icon>\n                </button>\n              </ion-col>\n              <ion-col col-3>\n                <button color="default" class="button-color-first" tooltip="Movimientos asignados" positionV="top" arrow *ngIf="current_list_shown == \'move_list\'  || current_list_shown == \'filtered_assigned\'  || current_list_shown == \'filtered_unassigned\'" [ngClass]="{\'active-icon\': current_list_shown == \'filtered_assigned\'}" (click)="moves_filter_by_assigned_pkgs(1)" outline icon-only>\n                  <ion-icon name=\'log-out\' is-active="true"></ion-icon>\n                </button>\n              </ion-col>\n            </ion-row>\n            <div if=lines_header *ngIf="current_list_shown == \'move_list\'  || current_list_shown == \'filtered_assigned\'  || current_list_shown == \'filtered_unassigned\'">\n              <ion-row class="row header">\n                <ion-col col-1 class="col">\n                  <ion-checkbox (ionChange)="multipleSelection($event)" [(ngModel)]="multipleSelectionMain"></ion-checkbox>\n                </ion-col>\n                <ion-col col-2 class="col">Pedido</ion-col>\n                <ion-col col-3 class="col">P.Entrada</ion-col>\n                <ion-col col-3 class="col">P.Salida</ion-col>\n                <ion-col col-3 class="col">\n                  Opc. \n                  <button tooltip="Añadir todo al paquete" positionV="top" class="row-button right-button" color="default" (click)="add_multiple_lines_to_package()" outline icon-only>\n                    <ion-icon name=\'add-circle\' is-active="true"></ion-icon>\n                  </button>\n                  <button tooltip="Desempaquetar todo" positionV="top" class="row-button right-button" color="default" (click)="add_multiple_lines_to_package(\'del\')" outline icon-only>\n                    <ion-icon name=\'remove-circle\' is-active="true"></ion-icon>\n                  </button>\n                </ion-col>\n              </ion-row>\n              <div dragula="move_lines_container" id="lines" [dragulaModel]="users_list">\n                <div *ngFor="let move of full_stock_moves" id="{{move[\'id\']}}" (press)="show_shipping_options_line(move[\'id\'])">\n                    <ion-row class="row" \n                    \n                    *ngIf="((move[\'shipping_type\'] && move[\'shipping_type\'] == current_shipping_type) || current_shipping_type == \'all\') && ((current_list_shown == \'filtered_unassigned\' && !move[\'result_package_id\']) || (current_list_shown == \'filtered_assigned\' && move[\'result_package_id\']) || (current_list_shown == \'move_list\'))">\n                      <ion-col col-12 \n                      [ngClass]="{\'pasaran-type\': move[\'shipping_type\'] && move[\'shipping_type\'] == \'pasaran\', \'route-type\': move[\'shipping_type\'] && move[\'shipping_type\'] == \'route\', \'urgent-type\': move[\'shipping_type\'] && move[\'shipping_type\'] == \'urgent\'}" \n                      class="col product-col"><strong>{{move[\'name\']}}</strong><strong class="product-units">{{move[\'product_qty\']}} Ud(s).</strong></ion-col>\n\n                      <ion-col col-1 class="col product-col shipping-color">\n                        <ion-checkbox (ionChange)="simpleSelection($event, move[\'id\'])" [(ngModel)]="move[\'isChecked\']"></ion-checkbox>\n                      </ion-col>\n                      <ion-col col-2 class="col product-col shipping-color">{{move[\'origin\']}}</ion-col>\n                      <ion-col col-3 class="col product-col shipping-color">{{move[\'package_id\'] && move[\'package_id\'][\'name\'] || \'N\'}}</ion-col>\n                      <ion-col *ngIf="move[\'result_package_id\'] && move[\'result_package_id\'][\'name\']; else not_result_package_id_open" \n                      col-3 class="col product-col shipping-color" [ngClass]="{\'active-icon\': move[\'result_package_id\'][\'id\'] == current_selected_pkg}" (click)="open_package(move[\'result_package_id\'][\'id\'])">{{move[\'result_package_id\'][\'name\']}}</ion-col>\n                      <ion-col col-3 class="col product-col options shipping-color">\n                        <ng-container [ngTemplateOutlet]="move[\'result_package_id\'] ?result_package_id_buttons : not_result_package_id_buttons" [ngTemplateOutletContext]="{move:move}"></ng-container>\n                      </ion-col>\n                      \n                    </ion-row>\n                  </div>\n              </div>\n            </div>\n            <div *ngIf="current_list_shown == \'package_list\'">\n              <ion-row class="row header">\n                <ion-col col-6 class="col">ID</ion-col>\n                <ion-col col-6 class="col">Nombre</ion-col>\n              </ion-row>\n              <div dragula="move_lines_container" id="arrival_pkgs" [dragulaModel]="current_partner_arrival_pkgs_list">\n                <ion-row class="row" *ngFor="let arrival_pkg of current_partner_arrival_pkgs_list" id="{{arrival_pkg[\'id\']}}">\n                  <ion-col col-6 class="col product-col">{{arrival_pkg[\'id\']}}</ion-col>\n                  <ion-col col-6 class="col product-col">\n                    {{arrival_pkg[\'name\']}}\n                    <button tooltip="Añadir al paquete" positionV="top" class="row-button right-button" color="default" (click)="add_package_content_to_package(arrival_pkg[\'id\'])" outline icon-only>\n                      <ion-icon name=\'add-circle\' is-active="true"></ion-icon>\n                    </button>\n                  </ion-col>\n                </ion-row>\n              </div>\n            </div>\n          </ion-scroll>\n        </ion-grid>\n      </ion-col>\n\n      <ion-col col-12 col-xs-12 col-sm-4 col-md-3 col-lg-4 col-xl-4>\n        <ion-row>\n          <ion-grid>\n            <ion-scroll scrollY=true>\n              <div *ngIf="current_selected_pkg == false">\n                <ion-row class="row header-reddish">\n                  <ion-col col-8 class="col pkg">\n                    Paquetes\n                  </ion-col>\n                  <ion-col col-4 class="col add">\n                    <ion-row>\n                    </ion-row>\n                  </ion-col>\n                </ion-row>\n                <ion-row class="row" dragula="move_lines_container" id="pkgs" [dragulaModel]="current_partner_pkg_list">\n                  <ion-col col-4 class="col fat-col" *ngFor="let pkg of current_partner_pkg_list" id="{{pkg[\'id\']}}" [ngClass]="{\'red-background\': pkg[\'id\'] == current_selected_pkg, \'hidden-col\': (!pkg[\'shipping_type\'] || (pkg[\'shipping_type\'] && pkg[\'shipping_type\'] != current_shipping_type)) && current_shipping_type != \'all\', \'pasaran-type\': pkg[\'shipping_type\'] == \'pasaran\', \'route-type\': pkg[\'shipping_type\'] == \'route\', \'urgent-type\': pkg[\'shipping_type\'] == \'urgent\'}" (click)="open_package(pkg[\'id\'])" (press)="show_shipping_options(pkg[\'id\'])">\n                    {{pkg[\'name\']}}\n                  </ion-col>\n                </ion-row>\n              </div>\n              <div *ngIf="current_selected_pkg != false">\n                <ion-row class="row header-reddish">\n                  <ion-col col-6 col-xs-12 col-sm-12 col-md-12 col-lg-6 col-xl-6 class="col pkg">\n                    {{current_pkg_data[\'name\']}}\n                  </ion-col>\n                  <ion-col col-6 col-xs-12 col-sm-12 col-md-12 col-lg-6 col-xl-6 class="col add">\n                    <ion-row>\n                      <button tooltip="Volver al listado" positionV="top" class="row-button black" icon-only (click)="reload_with_data(current_selected_partner, false, current_shipping_type)">\n                        <ion-icon name="undo"></ion-icon>\n                      </button>\n                      <button tooltip="Opciones de envío" positionV="top" class="row-button black" *ngIf="current_selected_partner && selected_partner_name && current_selected_pkg" icon-only (click)="show_shipping_options(current_selected_pkg)">\n                        <ion-icon name="cog"></ion-icon>\n                      </button>\n                      <button tooltip="Eliminar paquete" positionV="top" class="row-button black" *ngIf="current_selected_partner && selected_partner_name && current_selected_pkg" icon-only (click)="showDestroyConfirmation(current_selected_pkg)">\n                        <ion-icon name="remove-circle"></ion-icon>\n                      </button>\n                    </ion-row>\n                  </ion-col>\n                </ion-row>\n               \n                \n                <packaging-product id="{{packaging_line[\'id\']}}" *ngFor="let packaging_line of packaging_line_ids" [packaging_line] = "packaging_line"></packaging-product>\n                \n              \n               \n                <ion-row class="row header">\n                  <ion-col col-12 class="col add">\n                    <span *ngIf="current_selected_partner && selected_partner_name && current_selected_pkg">Envío: {{current_pkg_data[\'info_route_str\']}}</span>\n                  </ion-col>\n                </ion-row>\n                <div dragula="move_lines_container" id="pkgs_info" [dragulaModel]="current_pkg_info">\n                  <ion-row class="row" id="{{pkg_line[\'id\']}}" *ngFor="let pkg_line of current_pkg_info">\n                    <ion-col col-10 col-xs-6 col-sm-6 col-md-6 col-lg-10 col-xl-10 class="col product-col">\n                      <ion-row>{{pkg_line[\'name\']}}</ion-row>\n                    </ion-col>\n                    <ion-col col-2 col-xs-6 col-sm-6 col-md-6 col-lg-2 col-xl-2 class="col product-col">\n                      <ion-row>{{pkg_line[\'product_qty\']}} Ud(s)</ion-row>\n                    </ion-col>\n                  </ion-row>\n                </div>\n              </div>\n            </ion-scroll>\n          </ion-grid>\n        </ion-row>\n      </ion-col>\n    </ion-row>\n  </ion-grid>\n</ion-content>\n\n<!-- Else(s) -->\n\n<ng-template #not_selected_partner_name>\n  <ion-title>Movimientos de stock</ion-title>\n</ng-template>\n\n<ng-template #not_result_package_id_open>\n  <ion-col col-3 class="col product-col shipping-color">N</ion-col>\n</ng-template>\n\n<ng-template #result_package_id_buttons let-move=\'move\'>\n  <ion-row>\n    <button tooltip="Desempaquetar" class="row-button" positionV="top" arrow (click)="update_packages(move[\'id\'], false, \'unlink\')" color="default" outline icon-only>\n      <ion-icon name="remove-circle"></ion-icon>\n    </button>\n  </ion-row>\n</ng-template>\n\n<ng-template #not_result_package_id_buttons let-move=\'move\'>\n  <ion-row>\n    <button *ngIf="current_selected_pkg" tooltip="Añadir al paquete" positionV="top" class="row-button" color="default" (click)="update_packages(move[\'id\'])" outline icon-only>\n      <ion-icon name=\'add-circle\' is-active="true"></ion-icon>\n    </button>\n    <button *ngIf="!current_selected_pkg" tooltip="Opciones de envío" positionV="top" class="row-button" color="default" (click)="show_shipping_options_line(move[\'id\'])" outline icon-only>\n      <ion-icon name=\'cog\' is-active="true"></ion-icon>\n    </button>    \n  </ion-row>\n</ng-template>'/*ion-inline-end:"/home/kiko/ionic/packing_apk/src/pages/stock-move-list/stock-move-list.html"*/,
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
		454,
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
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_ionic_angular__ = __webpack_require__(41);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__ionic_storage__ = __webpack_require__(65);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__stock_move_list_stock_move_list__ = __webpack_require__(150);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__providers_odoo_odoo__ = __webpack_require__(125);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__providers_stock_stock__ = __webpack_require__(82);
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
        if (verificar) {
            this.cargar = true;
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
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__app_module__ = __webpack_require__(389);


Object(__WEBPACK_IMPORTED_MODULE_0__angular_platform_browser_dynamic__["a" /* platformBrowserDynamic */])().bootstrapModule(__WEBPACK_IMPORTED_MODULE_1__app_module__["a" /* AppModule */]);
//# sourceMappingURL=main.js.map

/***/ }),

/***/ 389:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return AppModule; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_platform_browser__ = __webpack_require__(42);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_ionic_angular__ = __webpack_require__(41);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__app_component__ = __webpack_require__(439);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__ionic_storage__ = __webpack_require__(65);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_ng2_dragula__ = __webpack_require__(227);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__components_packaging_product_packaging_product__ = __webpack_require__(449);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__pages_home_home__ = __webpack_require__(272);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8__pages_tabs_tabs__ = __webpack_require__(271);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_9__pages_stock_move_list_stock_move_list__ = __webpack_require__(150);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_10__ionic_native_status_bar_ngx__ = __webpack_require__(268);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_11__ionic_native_splash_screen_ngx__ = __webpack_require__(270);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_12__providers_stock_stock__ = __webpack_require__(82);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_13__providers_odoo_odoo__ = __webpack_require__(125);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_14__angular_platform_browser_animations__ = __webpack_require__(450);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_15_ionic_tooltips__ = __webpack_require__(452);
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
                __WEBPACK_IMPORTED_MODULE_7__pages_home_home__["a" /* HomePage */],
                __WEBPACK_IMPORTED_MODULE_8__pages_tabs_tabs__["a" /* TabsPage */],
                __WEBPACK_IMPORTED_MODULE_6__components_packaging_product_packaging_product__["a" /* PackagingProductComponent */],
                __WEBPACK_IMPORTED_MODULE_9__pages_stock_move_list_stock_move_list__["a" /* StockMoveListPage */]
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
                __WEBPACK_IMPORTED_MODULE_14__angular_platform_browser_animations__["a" /* BrowserAnimationsModule */],
                __WEBPACK_IMPORTED_MODULE_15_ionic_tooltips__["a" /* TooltipsModule */].forRoot()
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
                __WEBPACK_IMPORTED_MODULE_7__pages_home_home__["a" /* HomePage */],
                __WEBPACK_IMPORTED_MODULE_8__pages_tabs_tabs__["a" /* TabsPage */],
                __WEBPACK_IMPORTED_MODULE_9__pages_stock_move_list_stock_move_list__["a" /* StockMoveListPage */],
                __WEBPACK_IMPORTED_MODULE_6__components_packaging_product_packaging_product__["a" /* PackagingProductComponent */]
            ],
            providers: [
                __WEBPACK_IMPORTED_MODULE_10__ionic_native_status_bar_ngx__["a" /* StatusBar */],
                __WEBPACK_IMPORTED_MODULE_11__ionic_native_splash_screen_ngx__["a" /* SplashScreen */],
                __WEBPACK_IMPORTED_MODULE_12__providers_stock_stock__["a" /* StockProvider */],
                __WEBPACK_IMPORTED_MODULE_13__providers_odoo_odoo__["a" /* OdooProvider */],
                { provide: __WEBPACK_IMPORTED_MODULE_0__angular_core__["u" /* ErrorHandler */], useClass: __WEBPACK_IMPORTED_MODULE_2_ionic_angular__["d" /* IonicErrorHandler */] }
            ]
        })
    ], AppModule);
    return AppModule;
}());

//# sourceMappingURL=app.module.js.map

/***/ }),

/***/ 439:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return MyApp; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_ionic_angular__ = __webpack_require__(41);
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

/***/ }),

/***/ 449:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return PackagingProductComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__providers_stock_stock__ = __webpack_require__(82);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


var PackagingProductComponent = /** @class */ (function () {
    function PackagingProductComponent(stockInfo, changeDetectorRef) {
        this.stockInfo = stockInfo;
        this.changeDetectorRef = changeDetectorRef;
        console.log('Hello PackagingProductComponent Component');
        this.text = 'Hello World';
    }
    PackagingProductComponent.prototype.change_qty = function (qty) {
        if (qty == 1 || qty == -1) {
            this.packaging_line.qty += qty;
        }
        else if (+qty >= 0) {
            this.packaging_line.qty = qty;
        }
        else {
            this.packaging_line.qty = 0;
        }
        this.stockInfo.set_packaging_lines(this.packaging_line).then(function (val) {
        }).catch(function (mierror) {
            //this.stockInfo.presentAlert('Error de conexión', 'Error al recuperar los registros'+mierror + mierror)
            console.log(mierror);
        });
        this.changeDetectorRef.detectChanges();
    };
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["D" /* Input */])(),
        __metadata("design:type", Object)
    ], PackagingProductComponent.prototype, "packaging_line", void 0);
    PackagingProductComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["m" /* Component */])({
            selector: 'packaging-product',template:/*ion-inline-start:"/home/kiko/ionic/packing_apk/src/components/packaging-product/packaging-product.html"*/'<!-- Generated template for the PackagingProductComponent component -->\n\n\n\n  <ion-row>\n      <ion-col class="col">\n      <ion-label>\n        {{packaging_line.name}}\n      </ion-label>\n      </ion-col>\n  </ion-row>    \n  <ion-row>\n      <ion-col class="col tcenter remove" >\n        <button ion-button color="primary" (click)="change_qty(-1)">\n          <ion-icon name="remove-circle"></ion-icon>\n        </button>\n      </ion-col>\n      <ion-col class="col tcenter">\n        <ion-input [(ngModel)]="packaging_line.qty" (ionInput)="change_qty()" required name=\'qty\' class="tcenter" placeholder="Ingresa qty"></ion-input>\n      </ion-col>\n      <ion-col class="col add tcenter">\n        <button ion-button color="danger" (click)="change_qty(1)">\n          <ion-icon name="add-circle"></ion-icon>\n        </button>\n      </ion-col>\n  </ion-row>\n\n\n'/*ion-inline-end:"/home/kiko/ionic/packing_apk/src/components/packaging-product/packaging-product.html"*/
        }),
        __metadata("design:paramtypes", [__WEBPACK_IMPORTED_MODULE_1__providers_stock_stock__["a" /* StockProvider */], __WEBPACK_IMPORTED_MODULE_0__angular_core__["j" /* ChangeDetectorRef */]])
    ], PackagingProductComponent);
    return PackagingProductComponent;
}());

//# sourceMappingURL=packaging-product.js.map

/***/ }),

/***/ 82:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return StockProvider; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__(0);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__odoo_odoo__ = __webpack_require__(125);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_ionic_angular__ = __webpack_require__(41);
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
            'stock.move.line': {
                'tree': ['id', 'origin', 'name', 'result_package_id', 'move_id', 'product_qty', 'state', 'package_id', 'shipping_type'],
            },
            'stock.quant.package': {
                'tree': ['id', 'name', 'move_line_ids', 'shipping_type', 'delivery_carrier_id']
            },
            'stock.warehouse': {
                'form': ['id', 'name', 'company_id']
            },
            'delivery.carrier': {
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
    }
    // Package manager
    StockProvider.prototype.update_object = function (model, action, move_line_ids, package_id, result_package_id, partner_id) {
        if (model === void 0) { model = "stock.move.line"; }
        if (action === void 0) { action = false; }
        if (move_line_ids === void 0) { move_line_ids = []; }
        if (package_id === void 0) { package_id = false; }
        if (result_package_id === void 0) { result_package_id = false; }
        if (partner_id === void 0) { partner_id = false; }
        var self = this;
        var values = {
            'move_line_ids': move_line_ids,
            'package_id': package_id,
            'result_package_id': result_package_id,
            'action': action,
            'partner_id': partner_id
        };
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'update_object_from_apk', values).then(function (done) {
                console.log(done);
                resolve(done);
            })
                .catch(function (err) {
                console.log(err);
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
    StockProvider.prototype.set_packaging_lines = function (val) {
        var self = this;
        var model;
        model = 'stock.quant.package';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'set_packaging_lines', val).then(function (done) {
                resolve(done);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al actualizar set_packaging_lines");
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
    StockProvider.prototype.get_stock_move_lines_list_apk = function (partner_id, location_dest_id) {
        var self = this;
        var model;
        var values = {
            'location_dest_id': location_dest_id,
            'partner_id': partner_id
        };
        model = 'stock.move.line';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'get_apk_info_full', values).then(function (done) {
                resolve(done);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
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
    StockProvider.prototype.set_move_line_shipping_type = function (values) {
        var self = this;
        var model;
        model = 'stock.move.line';
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
    // Users list
    StockProvider.prototype.get_users_list_for_apk = function (location_dest_id) {
        var self = this;
        var model;
        var values = {
            'location_dest_id': location_dest_id
        };
        model = 'stock.move.line';
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
    StockProvider.prototype.get_users_list_for_apk_from_search_box = function (name) {
        var self = this;
        var model;
        var values = {
            'name': name
        };
        model = 'stock.move.line';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'get_users_list_for_apk_from_search_box', values).then(function (done) {
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
    StockProvider.prototype.get_routes_for_apk = function () {
        var self = this;
        var model;
        var values = {};
        model = 'delivery.route.path';
        var promise = new Promise(function (resolve, reject) {
            self.odooCon.execute(model, 'get_routes_for_apk', values).then(function (done) {
                resolve(done);
            })
                .catch(function (err) {
                reject(false);
                console.log("Error al validar");
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

/***/ })

},[274]);
//# sourceMappingURL=main.js.map