
import os
import sqlite3
import logging

logger = logging.getLogger(__name__)


def db_name():
    return path('swap.db')


def sqlite():
    return sqlite3.connect(db_name())


def clear(name, config=False):
    conn = sqlite()
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE swap=?', (name,))
    c.execute('DELETE FROM subjects WHERE swap=?', (name,))
    c.execute('DELETE FROM thresholds WHERE swap=?', (name,))
    if config:
        c.execute('DELETE FROM config WHERE swap=?', (name,))
    conn.commit()
    conn.close()
    


def create_db():
    conn = sqlite()
    conn.execute('CREATE TABLE users (swap,user,username,confusion)')
    conn.execute('CREATE TABLE subjects (swap,subject,gold,score,'
                 'retired,seen)')
    conn.execute('CREATE TABLE thresholds (swap,fpr,mdr,thresholds)')
    conn.execute('CREATE TABLE config (swap,config)')
    conn.close()


def list_config():
    conn = sqlite()
    c = conn.cursor()
    c.execute('SELECT * FROM config')
    return c.fetchall()


def dir():
    return os.path.abspath(os.path.dirname(__file__))


def path(fname):
    return os.path.join(dir(), fname)


if not os.path.isfile(db_name()):
    logger.info('Creating swap db')
    create_db()
