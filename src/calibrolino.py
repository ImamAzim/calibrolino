#!/usr/bin/env python

import os
import json
import sqlite3


import pytolino
import xdg_base_dirs


BOOK_TABLE_NAME ='books'
DATA_TABLE_NAME = 'data'
SERIES_TABLE_NAME = 'series'
BOOK_SERIES_LINK_NAME = 'books_series_link'


"""
select by format
collections
read status
file path
"""


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
        return db_path, db_folder
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

def create_books_dict(book_table, data_table, book_series_link_table, series_table):
    data_dict = {data['book']: data for data in data_table}
    book_dict = {book['id']: book for book in book_table}
    series_name = {serie['id']: serie['name'] for serie in series_table}
    series = {serie_link['book']: series_name[serie_link['series']] for serie_link in book_series_link_table}

    books = {book_id: (book, data_dict[book_id], series.get(book_id)) for book_id, book in book_dict.items()}

    return books

def get_all_tables(con, cur):
    book_table = get_table(con, cur, BOOK_TABLE_NAME)
    data_table = get_table(con, cur, DATA_TABLE_NAME)
    book_series_link_table = get_table(con, cur, BOOK_SERIES_LINK_NAME)
    series_table = get_table(con, cur, SERIES_TABLE_NAME)

    return book_table, data_table, book_series_link_table, series_table

def create_new_title(title, serie_index, serie_name):
    new_title = f'{serie_name}: {serie_index} - {title}'
    return new_title


def get_file_path(db_folder, book, data):
    sub_folder = book['path']
    filename = f"{data['name']}.{data['format'].lower()}"
    path = os.path.join(db_folder, sub_folder, filename)
    return path


def run():
    """ function to be executed as entry point to upload the data

    """
    print('a script to upload the calibre library')
    print('script not yet ready...')
    db_path, db_folder = get_calibre_db()
    con, cur = load_db(db_path)
    tables = get_all_tables(con, cur)

    books = create_books_dict(*tables)

    for book_id, (book, data, serie) in books.items():
        uuid = book['uuid']
        title = book['title']
        if serie is not None:
            serie_index = book['series_index']
            title = create_new_title(title, serie_index, serie)
            # print(title)
        book_path = get_file_path(db_folder, book, data)
        if not os.path.exists(book_path):
            raise FileNotFoundError('maybe the suffix is uppercase')


if __name__ == '__main__':
    run()
