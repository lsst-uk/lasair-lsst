import sys
sys.path.append('..')
import settings
import mysql.connector


def readonly():
    config = {
        'user'    : settings.DB_USER_READONLY,
        'password': settings.DB_PASS_READONLY,
        'host'    : settings.DB_HOST,
        'port'    : settings.DB_PORT,
        'database': 'ztf'
    }
    return mysql.connector.connect(**config)


def remote(allow_infile=False):
    config = {
        'user'    : settings.DB_USER_READWRITE,
        'password': settings.DB_PASS_READWRITE,
        'host'    : settings.DB_HOST,
        'port'    : settings.DB_PORT,
        'database': 'ztf'
    }
    if allow_infile:
        config['allow_local_infile'] = True
    return mysql.connector.connect(**config)


def local(database='ztf'):
    config = {
        'user'    : settings.LOCAL_DB_USER,
        'password': settings.LOCAL_DB_PASS,
        'host'    : settings.LOCAL_DB_HOST,
        'database': database
    }
    return mysql.connector.connect(**config)
