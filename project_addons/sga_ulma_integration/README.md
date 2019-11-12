# Intrucciones para Instalación de Oracle_fdw:

1. Instalamos las dependencias

sudo apt-get install postgresql-server-dev-all
sudo apt-get install postgresql-common

2. Seguimos la guía:

https://mikesmithers.wordpress.com/2011/04/03/oracle-instant-client-on-ubuntu-with-added-aliens/


3. Descargamos Oracle_fdw:

https://github.com/laurenz/oracle_fdw

4. Instalamos:

make
make install (si no tiene permisos utilizamos sudo)


# Intrucciones para conectar Postgresql con Oracle:

Paso 1: Oracle_fdw

racle_fdw es una extensión de PostgreSQL que implementa Foreign Data Wrapper para acceder a bases de datos de Oracle.
https://github.com/laurenz/oracle_fdw/releases/

Requisitos: https://github.com/laurenz/oracle_fdw#5-installation-requirements
PostgreSQL != 9.6.0 to 9.6.8 and 10.0 to 10.3
Oracle Instant Client/Oracle client >= 10.1

Instalación: https://github.com/laurenz/oracle_fdw#6-installation

Se puede usar este spec para crear un RPM: https://github.com/agapoff/RPM-specs/tree/master/oracle_fdw


Paso 2. Configurar el servidor remoto

Ejecutar bajo psql O CONFIGÚRALO DESDE ##Inventario->Configuración->Ajustes->Ulma database configuration## utilizando los botones en el orden adecuado.

CREATE EXTENSION IF NOT EXISTS oracle_fdw WITH SCHEMA public;

COMMENT ON EXTENSION oracle_fdw IS 'foreign data wrapper for Oracle';

CREATE SERVER oradb_my_server FOREIGN DATA WRAPPER oracle_fdw OPTIONS (dbserver '//my.ora.server:1521/SID');

CREATE USER MAPPING FOR my_postgres_user server oradb_my_server OPTIONS (password 'password', user 'userschema');

GRANT ALL PRIVILEGES ON FOREIGN DATA WRAPPER oracle_fdw TO my_postgres_user;

GRANT USAGE ON FOREIGN SERVER oradb_aserver_fire_cons TO my_postgres_user;

CREATE FOREIGN TABLE some_table ( field1 integer NOT NULL, field2 varchar(32) NOT NULL) SERVER oradb_my_server OPTIONS (TABLE 'ORA_TABLE'); <= Poner todas las columnas a las que necesites acceder respetando el orden de filas. Tendrás que sustituir mmmcod por ID si quieres agregar la tabla como modelo a Odoo.

En el modelo escribimos:
_auto = False
_table = foreign_table


## Modificar tablas

-- Si necesitas añadir columnas nuevas tendrás que crearlas en Oracle y luego agregarlas a tu foreing table en las mismas posiciones que en la tabla original.

ALTER FOREIGN TABLE foreign_table ADD COLUMN column_name data_type


# Fuente

http://agapoff.name/oracle-postgresql-links.html
https://github.com/laurenz/oracle_fdw#5-installation-requirements