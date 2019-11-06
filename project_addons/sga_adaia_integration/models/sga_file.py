# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta

import os

DELETE_FILE = False
ERRORS = 3
ODOO_READ_FOLDER = 'Send'
ODOO_END_FOLDER = 'Receive'
ODOO_WRITE_FOLDER = 'temp'

class AdaiaVars(models.Model):

    _name ='sgavar.file.var'
    _order = "sequence, id asc"

    sga_file_id = fields.Many2one("sgavar.file")
    sequence = fields.Integer("Sequence", defaul = 50)
    name = fields.Char("Campo Adaia")
    odoo_name = fields.Many2one("ir.model.fields",
                                domain="[('model_id','=',odoo_model)]",
                                string="Campo Odoo (si existe)" )
    odoo_model = fields.Many2one(related="sga_file_id.odoo_model")
    length = fields.Integer("Longitud", help="Campo numérico.")
    length_int = fields.Integer("L. Entera", help="Longitud entera(nº de digitos de la parte entera en un tipo 'float')")
    length_dec = fields.Integer("L. Decimal", help="Longitud decimal(nº de digitos de la parte decimal en un tipo 'float')")
    adaia_type = fields.Selection([('A', 'Alfanumerico'),
                                     ('N', 'Numerico'),
                                     ('B', 'Booleano'),
                                     ('D', 'Fecha'),
                                     ('H', 'Hora'),
                                     ('V', 'Atributo/Variable'),
                                     ('L', 'one2many'),
                                     ('R-A', 'Related-Alfanumérico'),
                                     ('R-N', 'Related-Numérico')])
    default = fields.Char("V. por defecto")
    fillchar = fields.Char("Caracter de relleno", size=1)
    required = fields.Boolean("Obligatorio", default=False)
    st = fields.Integer('Inicio cadena')
    en = fields.Integer('Fin cadena')


    @api.onchange('length','length_dec')
    def onchange_length(self):
        self.length_int = self.length - self.length_dec


class AdaiaFile(models.Model):

    _name = 'sgavar.file'

    def _get_name(self):
        for sgavar_file in self:
            sgavar_file.name = '%s/%s'%(sgavar_file.code, sgavar_file.version)

    name = fields.Char('Sga name', compute="_get_name")
    description = fields.Char('Sga file description')
    code = fields.Char('Sga file type', size=3)
    version = fields.Char("Version", size=2)
    odoo_model = fields.Many2one('ir.model', "Odoo Model")
    model = fields.Char(related='odoo_model.name')
    cte_name = fields.Char("Cte name")
    sga_file_var_ids = fields.One2many('sgavar.file.var', 'sga_file_id')
    version_active = fields.Boolean('Active')
    file_bytes = fields.Integer('Bytes')
    file_filter = fields.Char("Filter")
    _sql_constraints = [
        ('code_uniq', 'unique (code, version)', 'Este codigo/version de archivo ya existe!'),
    ]

    @api.constrains('version', 'version_active')
    def _check_active_version(self):
        domain = [('code', '=', self.code), ('version_active','=', True)]
        pool = self.search(domain)
        if len(pool) > 1:
            raise ValidationError("Solo puedes tener una version activa para coada codigo de fichero")

    @api.multi
    def write(self, vals):
        var_bytes = 0
        for var in self.sga_file_var_ids:
            var_bytes += var.length
        vals['file_bytes'] = var_bytes
        return super(AdaiaFile, self).write(vals)

    def reset_sequence(self):
        return
        domain = [('id', '!=', 0)]
        pool_files = self.env['sgavar.file'].search(domain)
        for pool in pool_files:
            min_id = 10000

            for var in pool.sga_file_var_ids:
                min_id = min(min_id, var.id)
            for var in pool.sga_file_var_ids:
                var.sequence = var.id - min_id
        return


    def update_positions(self):

        domain = [('id', '!=', 0)]
        pool_files = self.env['sgavar.file'].search(domain)
        for sga in pool_files:
            st=0
            en=0
            for var in sga.sga_file_var_ids:
                st = en
                en = st + var.length
                var.st = st
                var.en = en
        return True

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'version': int(self.version)+1
        })
        res = super(AdaiaFile, self).copy(default) 
        for var in self.sga_file_var_ids:
            var.copy({
                'sga_file_id': res.id
            })
        return res

class AdaiaFileHeader(models.Model):

    #Historico de ficheros donde guardar
    _name = "sga.file"

    name = fields.Char()
    sga_file = fields.Char('Fichero')  # ruta completa donde esta el archivo
    sga_path = fields.Char('Carpeta', default='', help="Carpeta del archivo")
    file_code = fields.Char('Codigo del fichero', size=3)

    state = fields.Selection([('W', 'En espera'), ('P', 'Procesado'), ('E', 'Error')])
    errors = fields.Integer('Errores', help="Numero de veces que debe aparecer el error antes de mover a error", default=1)
    file_type = fields.Selection ([(ODOO_READ_FOLDER, 'De Adaia a Odoo'), (ODOO_WRITE_FOLDER, 'De Odoo a Adaia')], string ="Tipo de fichero (I/O)", translate=True)

    file_time = fields.Datetime(string='Fecha/hora del archivo')
    version = fields.Integer('Version (Solo modo dev.)')

    log_name = fields.Char("Fichero log asociado")

    @api.model
    def set_file_name(self, file_type=False, version=False, file_date=False, prefix=False):

        if file_type and version and datetime == False:
            return False
        else:
            version = int(version)
            filename = u'%s%02d%02d%02d%02d%02d%02d' %(prefix,
                                                           file_date.year-2000,
                                                           file_date.month,
                                                           file_date.day,
                                                           file_date.hour,
                                                           file_date.minute,
                                                           file_date.second)
            return filename

    @api.model
    def archive_sga_files(self):
        import subprocess
        def create_month_dir(dir, frommonth=u'201801', move=True):

            start_date = '{}{}'.format(frommonth, u'01')
            str_from = datetime.strptime(start_date, '%Y%m%d')
            while str_from < (datetime.now() -timedelta(days=62)):
                dir_name = '{}{}{}'.format(dir, '%04d' % str_from.year, '%02d' % str_from.month)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                patt = '%04d%02d' % (str_from.year, str_from.month)

                str_from_1 = '{}{}'.format(dir,'?????{}*'.format(patt))
                str_from_2 = '{}{}'.format(dir,'{}??.*'.format(patt))
                str_to = '{}/'.format(dir_name)
                for str_from_ in [str_from_1, str_from_2]:
                    if move:
                        order = '{} {} {}'.format(command_move, str_from_, str_to)
                        subprocess.call(order, shell=True)
                    else:
                        order = '{} {}'.format(command_remove, str_from_)
                        subprocess.call(order, shell=True)

                str_from += timedelta(days=31)
                str_from -= timedelta(str_from.day-1)


        command_move = 'mv'
        command_remove = 'rm'

        #archive_files(delete=False)

        ICP = self.env['ir.config_parameter'].sudo()
        path = ICP.get_param('sga_adaia_integration.path_files', False)
        log_path = path + '/log'
        path_archive = u'%s/%s'%(path, 'archive')
        error_archive = u'%s/%s'%(path, 'error')
        temp_archive = u'%s/%s'%(path, 'temp')
        path_to_delete = [temp_archive]
        paths_to_archive = [log_path, error_archive, path_archive]
        for path in paths_to_archive:
            create_month_dir(path, move=True)

        for path in path_to_delete:
            create_month_dir(path, move=False)

        return True


    @api.model
    def get_sga_type(self, sga_filename):
        if sga_filename:
            file_prefix = sga_filename.rsplit('.', 1)[0]
            if file_prefix == 'TREXP':
                return 'BPP'
        else:
            return False

    @api.model
    def get_sga_version(self, sga_filename, version=False):
        if version:
            return version
        elif sga_filename:
            file_prefix = sga_filename.rsplit('.', 1)[0]
            if file_prefix == 'TREXP':
                return 0
        else:
            return False

    @api.model
    def get_file_time(self, sga_filename):
        try:
            sga_filename = sga_filename[sga_filename.find('.')+1:]
            return datetime(2000+ int(sga_filename[0:2]),
                            int(sga_filename[2:4]),
                            int(sga_filename[4:6]),
                            int(sga_filename[6:8]),
                            int(sga_filename[8:10]),
                            max(59, int(sga_filename[10:12])),
                            )
        except:
            return False

    @api.model
    def default_stage_id(self):
        return self.stage_id.get_default()

    def format_to_adaia_float(self, value, length_in=(12, 7, 5), default=0, fillchar='0'):

        length, length_int, length_dec = length_in
        value = value or fillchar
        # Comment if fill option
        value = str(value).split(".")

        return value[0]
        # Uncomment to fill
        #if not value:
        #    val = "0" * length
        #    return val

        #if length_dec == 0:
            # Formato entero
        #    val = '%s' % int(value)
        #    val = val.rjust(length, fillchar)
        #else:
            # Formato decimal
        #    value = float(value)
        #    int_ = int(value)
        #    dec_ = int((value - int_) * 10 ** length_dec)
        #    val = str(int_).rjust(length_int, fillchar)
        #    val += str(dec_).ljust(length_dec, fillchar)
        #return val

    def format_from_adaia_number(self, value, length_in=(12, 7, 5), default=False, fillchar='0'):
        length, length_int, length_dec = length_in
        value = str(value)
        if length_dec > 0:
            res = value[0:length_int] + '.' + value[length_int: length_int + length_dec]
            return float(res)
        else:
            res = value[0:length_int]
            return int(res)

    def format_to_adaia_date(self, date):

        return u'%04d%02d%02d%02d%02d%02d' % (
            date.year, date.month, date.day, date.hour, date.minute,
            date.second)

    def format_from_adaia_date(self, mec_date, long=True):

        if not mec_date:
            return False
        if long:
            return datetime(int(mec_date[0:4]),
                            int(mec_date[4:6]),
                            int(mec_date[6:8]),
                            int(mec_date[8:10]),
                            int(mec_date[10:12]),
                            int(mec_date[12:14]))

        else:
            return datetime(int(mec_date[0:4]),
                        int(mec_date[4:6]),
                        int(mec_date[6:8]))

    def write_log(self, str_log, log_name=False, header_line=True):

        def new_line(cadena):
            if len(cadena)> 1 and cadena[-1] != '\n':
                cadena = '{}\n'.format(cadena)
            return cadena

        try:

            if len(str_log)<= 1 and not header_line:
                return True

            if not log_name:
                log_name = u"%04d%02d%02d.log" % (datetime.now().year, datetime.now().month, datetime.now().day)

            ICP =self.env['ir.config_parameter'].sudo()
            path = ICP.get_param('sga_adaia_integration.path_files', False)
            log_folder = path + '/log'
            log_path = u'%s/%s'%(log_folder, log_name)            

            if not header_line:
                header = ''
            elif self:
                header = u'{} . {}\n'.format(datetime.now(), self.name)
            else:
                header = u'{}\n'.format(datetime.now())
            if not os.path.exists(log_path):
                self.touch_file(log_path)
            f = open(log_path, 'a')
            if f:
                if header_line and header != '':
                    str_log = u'%s >> %s\n' %(header, str_log)
                else:
                    str_log = '{}'.format(new_line(str_log))


                f.write(str_log)
                f.close()


        except:
            print("Error al escribir el log")
        return True

    def get_global_path(self):
        ICP =self.env['ir.config_parameter'].sudo()
        path = ICP.get_param('sga_adaia_integration.path_files', False)
        return path

    def create_new_sga_file_error(self, error_str):
        self.write_log(error_str)
        self.move_file('error')
        return False

    @api.model
    def create_new_sga_file(self, sga_filename, dest_path=ODOO_READ_FOLDER, create=True, version = 0):

        if create:
            prefix = sga_filename[:sga_filename.find('.')]
            sga_filename = sga_filename[sga_filename.find('.')+1:]
            sga_filename = prefix+'.%s%02d' % (sga_filename[0:17], version)
            domain = [('name', '=', sga_filename)]
            if self.env['sga.file'].search(domain):
                version += 1
                sga_filename = sga_filename[sga_filename.find('.')+1:]
                sga_filename = prefix+'.%s%02d'%(sga_filename[0:17], version)
                return self.create_new_sga_file(sga_filename, dest_path, create, version)

        path = self.get_global_path()
        sga_path = u'%s/%s'%(path, dest_path)
        error = False
        error_str = ''

        #if len(sga_filename) != 19 and len(sga_filename) != 23:
        #    error_str = u"Error en nombre de archivo: %s caracteres"% len(sga_filename)
        #    return self.create_new_sga_file_error(error_str)

        sga_file = os.path.join(sga_path, sga_filename)
        sga_type = self.get_sga_type(sga_filename)
        sga_file_time = self.get_file_time(sga_filename)
        if not sga_file_time:
            error_str = u"Error en la fecha de archivo %s " % sga_filename
            return self.create_new_sga_file_error(error_str)

        sga_state = 'W'
        vals = {
            'file_code': sga_type,
            'name': sga_filename,
            'sga_file': sga_file,
            'state': sga_state,
            'file_time': sga_file_time,
            'sga_path': sga_path,
            'log_name': u"%04d%02d%02d.log" % (datetime.now().year, datetime.now().month, datetime.now().day),
            'version': version
        }

        if create:
            error = self.touch_file(sga_file)
            if not error:
                error_str = "Error al acceder al archivo %s" % sga_file
                return self.create_new_sga_file_error(error_str)

        new_sga_file = self.create(vals)
        if not new_sga_file:
            error_str = "Error al crear SGA en la BD"
            return self.create_new_sga_file_error(error_str)

        self.write_log('Creado .... (%s)' % sga_filename)
        return new_sga_file

    @api.model
    def create(self, vals):

        sga_file = super(AdaiaFileHeader, self).create(vals)
        if sga_file:
            res = self.touch_file(sga_file.sga_file)
            if res:
                return sga_file
            else:
                raise ValidationError(_('Error al acceder/crear el archivo:\n%s.' % sga_file.sga_file))
        return sga_file

    def touch_file(self, sga_file):
        try:
            basedir = os.path.dirname(sga_file)
            if not os.path.exists(basedir):
                os.makedirs(basedir)
            if not os.path.exists(sga_file):
                with open(sga_file, 'a'):
                    os.utime(sga_file, None)
        except:
            return False
        return True

    @api.model
    def check_sga_name(self, filename, path):
        # compruebo que el fichero no este en la bd.
        # si esta lo borro y creo uno nuevo
        self.write_log("Proceso ... (%s)" % filename)
        domain = [('name', '=', filename)]
        sga_file = self.env['sga.file'].search(domain)
        if sga_file:
            sga_file.unlink()
        sga_file = self.create_new_sga_file(filename, ODOO_READ_FOLDER, create=False)
        if not sga_file:
            error_str = 'Error al crear %s en la BD' % filename
            self.env['sga.file'].write_log(error_str)
            return False

        return sga_file

    def import_file_from_adaia(self, file_code = False):
        process = []
        proc_error = False
        try:
            if self.file_code == "BPP":
                self.write_log("Desde adaia picking BPP ...")
                #process = self.env['stock.picking'].import_adaia_OUT(self.id)
                process = self.env['stock.batch.picking'].import_adaia_OUT(self.id)

            if process:
                self.move_file('archive', self.name)
                self.write_log("-- OK >> %s" % self.sga_file)
            else:
                proc_error = True
                self.write_log("-- ERROR >> %s\n--------------\n%s\n----------------------\n" %(self.sga_file, process))
        except:
            proc_error = True
            self.write_log("-- ERROR >> %s\n--------------\n%s\n----------------------\n" % (self.sga_file, "Error de archivo. No se puede mover"))

        if not process:
            self.move_file('error', self.name)
        return process

    #este es la accion que recorre la carpeta de ficheros provenientes del SGA
    def sga_process_file_xmlrpc(self):
        return self.process_sga_files()

    def process_sga_files(self, file_type=False, folder=ODOO_READ_FOLDER):

        res_file = False
        global_path = u'%s/%s' %(self.get_global_path(), folder)
        #self.write_log("Buscando ficheros en >> %s" % global_path)
        pool_ids = []
        for path, directories, files in os.walk(global_path, topdown=False):
            for name in files:
                file_prefix = name.rsplit('.', 1)[0]
                if file_type:
                    if file_code != file_type:
                        continue

                sga_file = self.check_sga_name(name, path)
                if sga_file:
                    str = "\n-------- Importando fichero: {} de tipo {}\n".format(sga_file.name, file_prefix)
                    self.write_log(str)
                    pool_id = sga_file.import_file_from_adaia(file_code=file_prefix)
                if file_type:
                    pool_ids.append(pool_id)

        return pool_ids

    def move_file(self, folder, file_name=False):
        new_path = False
        try:
            new_path = u'%s/%s' % (self.get_global_path(), folder)
            new_name = os.path.join(new_path, self.name)
            os.rename(self.sga_file, new_name)
            self.sga_file = new_name
            self.sga_path = new_path
            self.write_log("-- Movemos  >> %s a %s" %(self.name, new_path))
        except:
            self.write_log("-- Error al mover >> %s a %s" %(self.name, new_path))


    def create_global_PST(self):
        data_file = datetime.now()
        sga_file_name = self.set_file_name("PST", 3, data_file)
        new_sga_file = self.create_new_sga_file(sga_file_name, ODOO_WRITE_FOLDER, create=True)
        if new_sga_file:
            f = open(new_sga_file.sga_file, 'a')
            if f:
                file_str = "PLS".ljust(265, " ") + "T"
                f.write(file_str)
                f.close()
                path = self.get_global_path()

                sga_path = u'%s/%s' % (path, ODOO_WRITE_FOLDER)
                old_name = f.name  # os.path.join(sga_path, f.name)

                sga_path = u'%s/%s' % (path, ODOO_END_FOLDER)
                new_name = old_name.replace(ODOO_WRITE_FOLDER, ODOO_END_FOLDER)

                # cambio permisos
                # os.chmod(old_name, stat.S_IXUSR)
                os.rename(old_name, new_name)
                # os.chmod(new_name, stat.S_IXOTH)

            else:
                raise ValidationError("Error al escribir los datos en %s" % new_sga_file.sga_file)


    @api.multi
    def check_sga_file(self, model, ids=[], code=False, create=True, version=False):
        # code = False,  version = False, field_list = False, field_ids = False, field_list_ids = False):
        # model modelo principal
        # ids si se especifica recorre solo estos id,
        # create fuerza la creacion del fichero
        # code codigo de aplicacion del fichero
        # version version del fichero
        # field_list lista de campos/longitud que a generar

        # field_ids si tiene lista de filas (sale_order_line estan en este campo
        # con la lista de campos/longitud field_list_ids

        def get_line(sgavar, model_pool):
            # TODO Revisar si hace falta contador para los
            # todo numeros de lineas o vale el id de los _ids
            cont = 0
            res = ''
            if sgavar.file_filter:
                model_pool = model_pool.filtered(eval(sgavar.file_filter))
            for model in model_pool:

                cont += 1
                model_str = ''
                var_str = ''
                try:
                    new_sga_file.write_log('    Modelo: {} >> {}'.format(model, model.name), header_line=False)
                except:
                    new_sga_file.write_log('    Modelo: {}'.format(model), header_line=False)

                for val in sgavar.sga_file_var_ids:
                    line_ids = False

                    value = False
                    length = [val.length, val.length_int, val.length_dec]

                    # Si viene en el context forzada la variable
                    if self._context.get(val.name, False):
                        var_str = self.odoo_to_adaia(self._context.get(val.name),
                                                       length, val.adaia_type, val.default, val.fillchar)

                    # Si es un atributo >>> debe tener asignado un campo en odoo o es []
                    elif val.adaia_type == "V":
                        if val.odoo_name:
                            value = u'[%s]' % model[val.odoo_name.name]
                        else:
                            value = u'[]'
                        var_str = value

                    #No es listado de líneas
                    elif val.adaia_type != "L":
                        if val.name == "num_lim" and not val.odoo_name:
                            value = cont
                        elif val.odoo_name:
                            value = model[val.odoo_name.name]
                            if val.adaia_type == "R-A" or val.adaia_type == "R-N":
                                value = value[val.default]

                        if not value and val.required:
                                value = val.default

                        if value == '' and not val.default:
                            raise UserError("Revisa la configuracion del campo %s del modelo %s"%(val.name, val.sga_file_id))

                        var_str = self.odoo_to_adaia(value, length, val.adaia_type, val.default, val.fillchar)
                    else:
                        # Listado de lineas
                        new_model = model[val.odoo_name.name]
                        new_sgavar = self.env['sgavar.file'].search([('code', '=', val.default)], limit=1)
                        if new_sgavar.file_filter:
                            new_model = new_model.filtered(eval(new_sgavar.file_filter))
                        value = len(new_model) or 0
                        var_str = self.odoo_to_adaia(value, length, val.adaia_type, val.default, val.fillchar)
                        line_ids = True

                    if not line_ids:
                        model_str += var_str.strip()+'|'
                    # Esta es para el formato seguido sin separador.
                    #model_str += var_str 
                res += model_str + '\n'

                if line_ids:
                    res += get_line(new_sgavar, new_model)
            return res

        domain = [('code', '=', code)]
        if version:
            domain += [('version', '=', version)]
        sgavar = self.env['sgavar.file'].search(domain, limit=1)

        if not sgavar:
            return
            raise ValidationError("No se ha encontrado un modelo para ese tipo de fichero %s" % code)

        if not ids:
            return
            raise ValidationError("No se ha encontrado ningun registro para procesar")
        model_pool = self.env[model].browse(ids)

        if not model_pool:
            raise ValidationError("No se ha encontrado ningun registro de %s" % model)

        data_file = datetime.now()
        prefix = self._context.get('PREFIX', False)
        sga_file_name = self.set_file_name(sgavar.code, sgavar.version, data_file, prefix)
        if not sga_file_name:
            raise ValidationError("Error en el nombre del fichero")

        new_sga_file = self.create_new_sga_file(sga_file_name, ODOO_WRITE_FOLDER, create=create)

        if not new_sga_file:
            raise ValidationError("Error. Revisa el fichero del log para mas detalles")
        hora_inicio=datetime.now()
        new_sga_file.write_log('    Fichero {}\n    Hora inicio: {}'.format(new_sga_file.name, datetime.now()), header_line=False)

        if new_sga_file:
            f = open(new_sga_file.sga_file, 'a')
            if f:
                file_str = get_line(sgavar, model_pool)
                f.write(file_str)
                f.close()

                path = self.get_global_path()

                sga_path = u'%s/%s' % (path, ODOO_WRITE_FOLDER)
                old_name = f.name # os.path.join(sga_path, f.name)

                sga_path = u'%s/%s' % (path, ODOO_END_FOLDER)
                new_name = old_name.replace(ODOO_WRITE_FOLDER, ODOO_END_FOLDER)

                #cambio permisos
                #os.chmod(old_name, stat.S_IXUSR)
                os.rename(old_name, new_name)
                #os.chmod(new_name, stat.S_IXOTH)

            else:
                raise ValidationError("Error al escribir los datos en %s" % new_sga_file.sga_file)
        new_sga_file.write_log('    Hora fin: {}. Tiempo empleado: {}'.format(datetime.now(), datetime.now()-hora_inicio), header_line=False)
        return new_sga_file

    def odoo_to_adaia(self, value, length_in, adaia_type, default=False, fillchar=False):


        def type_A(value):
            # Tipo string
            if not default and not value:
                val = " " * length_int
            else:
                new_val = '%s' %(value or default)
                # Uncomment to fill with 0
                val = new_val
                #val = new_val.ljust(length_int, fillchar)
            # We need to replace all the line breaks
            val = val.replace('\n', ' ').replace('\r', '')
            return val

        def type_B(value):
            # Tipo string
            if value == "1" or value is True:
                new_val = "1"
            elif value == "0" or value is False:
                new_val = "0"
            else:
                new_val = " "
            return new_val

        def type_N(value):
            val = self.format_to_adaia_float(value, length_in, fillchar)
            return val

        length, length_int, length_dec = length_in
        fillchar = str(fillchar)

        if adaia_type == 'A':
            # Adaia alphanumeric
            return type_A(value)[0:length_int]

        elif adaia_type == 'B':
            # Adaia Boolean
            if value == "":
                value == default or fillchar

            return type_B(value)

        elif adaia_type == 'N':
            # Adaia Numeric
            return type_N(value)

        elif adaia_type == 'L':
            # One2many, pero es Adaia Numeric
            return type_N(value)

        elif adaia_type == "D":
            if value:
                value = datetime.strptime(value, tools.DEFAULT_SERVER_DATETIME_FORMAT).strftime('%Y%m%d')
            else:
                value = ''
            # Adaia date
            return type_A(value)

        elif adaia_type == 'H':
            if value:
                value = datetime.strptime(value, tools.DEFAULT_SERVER_DATETIME_FORMAT).strftime('%H%M')
            else:
                value = ''
            # Adaia date
            return type_A(value)

        elif adaia_type == 'R-A':
            if not value:
                value = ' '
            # Adaia alphanumeric
            return type_A(value)
        
        elif adaia_type == 'R-N':
            # Adaia numeric
            return type_N(value)

        elif adaia_type == "V":
            # Adaia Atribute
            return ''
        else:
            return ''


class AdaiaFileLine(models.Model):
    _name = "sga.file.line"

    sga_file_id = fields.Many2one('sga.file')
    stock_move_id = fields.Many2one("stock.move")
    line = fields.Char('File line')
    name = fields.Char('Line name')