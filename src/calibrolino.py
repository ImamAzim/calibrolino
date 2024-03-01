#!/usr/bin/env python

import os
import json
import sqlite3


import pytolino
import xdg_base_dirs


"""
read status
"""


class Calibrolino(object):

    """prepare and upload the calibre library to the cloud"""
    calibre_db_table = dict(
            books='books',
            data='data',
            series='series',
            books_series_link='books_series_link',
            tags='tags',
            books_tags_link='books_tags_link',
            authors='authors',
            books_authors_link='books_authors_link',
            custom_columns='custom_columns',
            )

    calibre_column_status_name = 'statut'

    def __init__(self,
            accepted_formats={'EPUB'},
            column_status_name='status',
            ):
        """
        column_status_name: the name of a custom column in calibre that tells if the book is Read or not.
        """
        self.accepted_formats = accepted_formats
        self.column_status_name = column_status_name

    def _get_calibre_db(self):
        """search in home calibre db

        """
        calibre_config_fn = 'global.py.json'
        calibre_folder = 'calibre'
        db_fn = 'metadata.db'
        library_config_key = 'library_path'
        folder = os.path.join(xdg_base_dirs.xdg_config_home(), calibre_folder)
        calibre_config_path = os.path.join(folder, calibre_config_fn)
        with open(calibre_config_path) as myfile:
            config = json.load(myfile)

        self.db_folder = config[library_config_key]
        self.db_path = os.path.join(self.db_folder, db_fn)

    def _load_db(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        con.row_factory = sqlite3.Row

        self.con = con
        self.cur = cur


    def _get_table(self, table_name):
        """load the book table from the calibre db


        """
        sql = f'SELECT * from {table_name}'
        res = self.con.execute(sql)
        table = res.fetchall()

        return table

    def get_all_tables(self):

        self.tables = dict()

        for table_name in self.calibre_db_table.keys():
            self.tables[table_name] = self._get_table(self.calibre_db_table[table_name])

        custom_column_id = None
        for custom_column in self.tables['custom_columns']:
            if custom_column['name'] == self.column_status_name:
                custom_column_id = custom_column['id']
        if custom_column_id is not None:
            self.status_table_name = f'custom_column_{custom_column_id}'
            self.status_link_table_name = f'books_custom_column_{custom_column_id}_link'
            table_names = self.status_table_name, self.status_link_table_name
            for table_name in table_names:
                self.tables[table_name] = self._get_table(self.calibre_db_table[table_name])
            self.status_is_defined = True
        else:
            self.status_is_defined = False

    def _create_books_dict(self):
        data_dict = {data['book']: data for data in self.tables['data']}
        book_dict = {book['id']: book for book in self.tables['books']}

        series_name = {serie['id']: serie['name'] for serie in self.tables['series']}
        collection_names = {collection['id']: collection['name'] for collection in self.tables['tags']}
        authors_names = {author['id']: author['name'] for author in self.tables['authors']}

        series = {serie_link['book']: series_name[serie_link['series']] for serie_link in self.tables['books_series_link']}
        collections = {collection_link['book']: collection_names[collection_link['tag']] for collection_link in self.tables['books_tags_link']}

        authors = dict()
        for author_link in self.tables['books_authors_link']:
            book = author_link['book']
            author_id = author_link['author']
            author_name = authors_names[author_id]
            if book not in authors:
                authors[book] = [author_name]
            else:
                authors[book].append(author_name)

        books = {book_id: (
            book,
            data_dict[book_id],
            series.get(book_id),
            collections.get(book_id),
            authors.get(book_id),
            )
            for book_id, book in book_dict.items()}

        self.books = books


    def _create_new_title(self, title, serie_index, serie_name):
        new_title = f'{serie_name}: {serie_index} - {title}'
        return new_title


    def _get_file_path(self, book, data):
        sub_folder = book['path']
        filename = f"{data['name']}.{data['format'].lower()}"
        path = os.path.join(self.db_folder, sub_folder, filename)
        return path


    def run(self):
        print('a script to upload the calibre library')
        print('script not yet ready...')
        self._get_calibre_db()
        self._load_db()
        self.get_all_tables()

        self._create_books_dict()

        for book_id, (book, data, serie, collection, authors) in self.books.items():
            book_format = data['format']
            if book_format.upper() in self.accepted_formats:
                uuid = book['uuid']
                title = book['title']
                if serie is not None:
                    serie_index = book['series_index']
                    title = self._create_new_title(title, serie_index, serie)
                    # print(title)
                book_path = self._get_file_path(book, data)
                if not os.path.exists(book_path):
                    raise FileNotFoundError('maybe the suffix is uppercase')
                print(title, collection, authors)

def run():
    """ function to be executed as entry point to upload the data

    """
    my_calibrolino = Calibrolino()
    my_calibrolino.run()


if __name__ == '__main__':
    run()
