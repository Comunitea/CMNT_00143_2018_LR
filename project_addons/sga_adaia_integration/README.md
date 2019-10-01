# Cargar datos de los CSV

- 1º: La tabla sgavar_file debe estar vacía, es decir el módulo debe estar recién instalado, de lo contrario sgafile var no encontrará los ids de sgafile.
- 2º: Cargamos el model sgafile, en Odoo Model debemos seleccionar id externo.
- 3º: Cargamos el model sgafile var, en Campo Odoo (si existe) seleccionamos external id, en Odoo Model seleccionamos también external id y en Sga File seleccionamos database id.


# Comprobaciones

- 1º El picking type debe estar configurado con el tipo de sga, el tipo de archivo y el prefijo con el que se guarda.