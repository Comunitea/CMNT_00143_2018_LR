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

Ejecutar bajo psql:

CREATE EXTENSION IF NOT EXISTS oracle_fdw WITH SCHEMA public;

COMMENT ON EXTENSION oracle_fdw IS 'foreign data wrapper for Oracle';

CREATE SERVER oradb_my_server FOREIGN DATA WRAPPER oracle_fdw OPTIONS (dbserver '//my.ora.server:1521/SID');

CREATE USER MAPPING FOR my_postgres_user server oradb_my_server OPTIONS (password 'password', user 'userschema');

GRANT ALL PRIVILEGES ON FOREIGN DATA WRAPPER oracle_fdw TO my_postgres_user;

GRANT USAGE ON FOREIGN SERVER oradb_aserver_fire_cons TO my_postgres_user;

CREATE FOREIGN TABLE some_table ( field1 integer NOT NULL, field2 varchar(32) NOT NULL) SERVER oradb_my_server OPTIONS (TABLE 'ORA_TABLE'); <= Poner todas las columnas a las que necesites acceder.

## Integración con Odoo

-- Se puede configurar automáticamente introduciendo los datos desde Inventario->Configuración->Ajustes->Ulma database configuration y utilizando los botones en el orden adecuado.

-- Si necesitas añadir las tablas como un modelo entonces deben tener las tablas propias de Odoo (id, create_date, write_id, create_uid y write_uid),
en caso de que no las tenga tendrás que crearlas en Oracle y luego agregarlas a tu foreing table.

ALTER FOREIGN TABLE foreign_table ADD COLUMN id SERIAL
ALTER FOREIGN TABLE foreign_table ADD COLUMN create_date timestamp without time zone
ALTER FOREIGN TABLE foreign_table ADD COLUMN write_date timestamp without time zone
ALTER FOREIGN TABLE foreign_table ADD COLUMN create_uid integer
ALTER FOREIGN TABLE foreign_table ADD COLUMN write_uid integer

En el modelo escribimos:
_auto = False
_table = foreign_table


# Fuente

http://agapoff.name/oracle-postgresql-links.html
https://github.com/laurenz/oracle_fdw#5-installation-requirements