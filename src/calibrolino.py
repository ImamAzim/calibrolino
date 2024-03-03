#!/usr/bin/env python

import os
import json
import sqlite3
import sys


import pytolino
import xdg_base_dirs


class CalibreDBReader(object):

    """prepare and upload the calibre library to the cloud"""
    _calibre_db_table = [
            'books',
            'data',
            'series',
            'books_series_link',
            'tags',
            'books_tags_link',
            'authors',
            'books_authors_link',
            'publishers',
            'books_publishers_link',
            'languages',
            'books_languages_link',
            'custom_columns',
            ]

    def __init__(self):
        """
        finds the calibre db and connect to it
        """

        self._get_calibre_db()
        self._load_db()

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

        self._db_folder = config[library_config_key]
        self._db_path = os.path.join(self._db_folder, db_fn)

        if not os.path.exists(self._db_path):
            raise FileExistsError(
                    'could not found the calibre db. is calibre installed?')

    def _load_db(self):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()
        con.row_factory = sqlite3.Row

        self._con = con
        self._cur = cur

    def _get_table(self, table_name):
        """load the book table from the calibre db


        """
        sql = f'SELECT * from {table_name}'
        res = self._con.execute(sql)
        table = res.fetchall()

        return table

    def _get_all_tables(self):

        self._tables = dict()

        for table_name in self._calibre_db_table:
            self._tables[table_name] = self._get_table(table_name)

        custom_column_id = None
        for custom_column in self._tables['custom_columns']:
            if custom_column['name'] == self._column_status_name:
                custom_column_id = custom_column['id']
        if custom_column_id is not None:
            self._status_table_name = f'custom_column_{custom_column_id}'
            table_names = self._status_table_name, self._status_link_table_name
            for table_name in table_names:
                self._tables[table_name] = self._get_table(table_name)
            self._status_is_defined = True
        else:
            self._status_is_defined = False

    def _create_books_dict(self):

        files_data = {row['book']: row for row in self._tables['data']}

        data_names = dict()
        metadata = dict()
        datas = [
                ('series', 'name', 'series'),
                ('tags', 'name', 'tag'),
                ('authors', 'name', 'author'),
                ('publishers', 'name', 'publisher'),
                ('languages', 'lang_code', 'lang_code'),
                ]
        if self._status_is_defined:
            datas.append(
                    (self._status_table_name, 'value' 'value')
                    )
        for data, column_name0, column_name in datas:
            data_names[data] = dict()
            for row in self._tables[data]:
                data_names[data][row['id']] = row[column_name0]
            metadata[data] = dict()
            table_link_name = f'books_{data}_link'
            for row in self._tables[table_link_name]:
                book_id = row['book']
                data_id = row[column_name]
                metadata_value = data_names[data][data_id]
                if book_id not in metadata[data]:
                    metadata[data][book_id] = [metadata_value]
                else:
                    metadata[data][book_id].append(metadata_value)

        self._books = list()

        for book_row in self._tables['books']:
            book_id = book_row['id']
            file_data = files_data[book_id]
            file_path=self._get_file_path(book_row, file_data),
            serie_name=metadata['series'].get('book_id')
            if serie_name is not None:
                serie_name = serie_name[0]
            if self._status_is_defined:
                status = metadata[self._status_table_name].get(book_id)
            else:
                status = None
            cover_path = self._get_cover_path(book_row, file_data)

            book = dict(
                    title=book_row['title'],
                    authors=metadata['authors'].get(book_id),
                    uuid=book_row['uuid'],
                    file_path=file_path,
                    publishers=metadata['publishers'].get(book_id),
                    series_index=book_row['series_index'],
                    serie_name=serie_name,
                    tags=metadata['tags'].get(book_id),
                    status=status,
                    isbn=book_row['isbn'],
                    pubdate=book_row['pubdate'],
                    languages=metadata['languages'].get(book_id),
                    cover_path=cover_path,
                    )
            self._books.append(book)


    def get_serie_title(self, title, serie_index, serie_name):
        new_title = f'{serie_name}: {serie_index} - {title}'
        return new_title


    def _get_file_path(self, book, data):
        sub_folder = book['path']
        filename = f"{data['name']}.{data['format'].lower()}"
        path = os.path.join(self._db_folder, sub_folder, filename)
        return path

    def _get_cover_path(self, book, data):
        sub_folder = book['path']
        filename = 'cover.jpg'
        path = os.path.join(self._db_folder, sub_folder, filename)
        return path

    def read_db(self,
            accepted_formats={'EPUB'},
            column_status_name='statut',
            ):
        """
        load the calibre db and create a list of the books with metadata
        :column_status_name: the name of a custom column in calibre that tells if the book is Read or not.
        :returns: books: dict

        """
        self._accepted_formats = accepted_formats
        self._column_status_name = column_status_name

        self._get_all_tables()
        self._create_books_dict()

        return self._books

        # for book_id, (book, data, serie, collection, authors, status) in self.books.items():
            # book_format = data['format']
            # if book_format.upper() in self.accepted_formats:
                # uuid = book['uuid']
                # title = book['title']
                # if serie is not None:
                    # serie_index = book['series_index']
                    # title = self._create_new_title(title, serie_index, serie)
                    # # print(title)
                # book_path = self._get_file_path(book, data)
                # if not os.path.exists(book_path):
                    # raise FileNotFoundError('maybe the suffix is uppercase')
                # print(title, status)

def run():
    """ function to be executed as entry point to upload the data

    """
    pass
    # my_calibrolino = Calibrolino()
    # my_calibrolino.run()


if __name__ == '__main__':
    calibre_db = CalibreDBReader()
    books = calibre_db.read_db()
    for book in books:
        print('==========')
        for key, value in book.items():
            print(f'{key}: {value}')
