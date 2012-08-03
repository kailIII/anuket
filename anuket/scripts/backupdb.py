# -*- coding: utf-8 -*-
import os
import argparse
import bz2
import logging
import sqlite3
from datetime import date

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging


log = logging.getLogger(__name__)


def verify_directory(dir):
    """ Create and/or verify the existence of a filesystem directory."""
    if not os.path.exists(dir):
        try:
            os.makedirs(dir, 0775)
        except:
            raise


#def dump_mysql():
#    """ Dump a MySQL database."""
#    pass

def dump_sqlite(connect_args):
    """ Dump a SQLite database."""
    con = sqlite3.connect(connect_args['database'])
    sql_dump = os.linesep.join(con.iterdump())
    con.close()
    return sql_dump

#def dump_postgresql():
#    """ Dump a PostgreSQL database."""
#    pass


def bzip(sql_dump, backup_directory, brand_name, overwrite=False):
    """ Compress the SQL dump with bzip2 and save the file."""
    today = date.today().isoformat()
    filename = '{0}-{1}.sql.bz2'.format(brand_name, today)
    path = os.path.join(backup_directory, filename)
    # check if the file already exist
    isfile = os.path.isfile(path)
    if not isfile or overwrite:
        # create the zipped dump
        bz = bz2.BZ2File(path, 'w')
        bz.write(sql_dump)
        bz.close()
        log.info("Database dump done")
    else:
        message = "There is already a database backup with the same name!"
        log.error(message)
        return message


def backup_db(config_uri=None, overwrite=False):
    setup_logging(config_uri)
    # get the setting from the config file
    settings = get_appsettings(config_uri)
    brand_name = settings['anuket.brand_name']
    backup_directory = settings['anuket.backup_directory']
    # verify and/or create the backup directory
    log.info("Checking the backup directory")
    verify_directory(backup_directory)
    # get db engine from settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    connect_args = engine.url.translate_connect_args()
    if engine.dialect.name == 'sqlite':
        log.info("Dump the SQLite database")
        sql_dump = dump_sqlite(connect_args)
#    if engine.dialect.name == 'mysql':
#        pass
#    if engine.dialect.name == 'postgresql':
#        pass
    else:
        message = "Unsuported database engine!"
        log.error(message)
        print(message)
    if sql_dump:
        log.info("Compress and save the database dump")
        bzip(sql_dump, backup_directory, brand_name, overwrite)


def main():  # pragma: no cover
    """Dump the database for backup purpose.

    Supported database: SQLite.
    """
    # get option from command line
    parser = argparse.ArgumentParser(
        description='Dump the database',
        usage='%(prog)s config_file.ini',
        epilog='example: %(prog)s developement.ini')
    parser.add_argument('config_file',
        nargs='?',
        help='the application config file')
    parser.add_argument('-o', '--overwrite', action='store_true',
        help='overwrite existing backups files if set')
    args = parser.parse_args()

    if not args.config_file:
        # display the help message if no config_file is provided
        parser.print_help()
    else:
        backup_db(args.config_file, args.overwrite)


#TODO: this is a very simple script we need to :
#Add other dadatases support (MySQL and Postgres)
