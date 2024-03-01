#!/usr/bin/env python

import os
import json
import sqlite3


import pytolino
import xdg_base_dirs


BOOK_TABLE_NAME ='books'
DATA_TABLE_NAME = 'data'


def get_calibre_db():
    """search in home calibre db
    :returns: path to calibre db

    """
    calibre_config_fn = 'global.py.json'
    calibre_folder = 'calibre'
    db_fn = 'metadata.db'
    library_config_key = 'library_path'
    folder = os.path.join(xdg_base_dirs.xdg_config_home(), calibre_folder)
    calibre_config_path = os.path.join(folder, calibre_config_fn)
    with open(calibre_config_path) as myfile:
        config = json.load(myfile)
    db_folder = config[library_config_key]
    db_path = os.path.join(db_folder, db_fn)
    if os.path.exists(db_path):
        return db_path
    else:
        return None


def load_db(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    con.row_factory = sqlite3.Row
    return con, cur


def get_table(con, cur, table_name):
    """load the book table from the calibre db

    :cur: cursor connecting the calibre db
    :returns: list of books

    """
    sql = f'SELECT * from {table_name}'
    res = con.execute(sql)
    books = res.fetchall()

    return books


def run():
    """ function to be executed as entry point to upload the data

    """
    print('a script to upload the calibre library')
    print('script not yet ready...')
    db_path = get_calibre_db()
    con, cur = load_db(db_path)
    books = get_table(con, cur, BOOK_TABLE_NAME)
    for book in books:
        print(book['title'])


if __name__ == '__main__':
    run()
