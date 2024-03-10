#!/usr/bin/env python

import os
import json
import sqlite3
import sys


from pytolino.tolino_cloud import Client, PytolinoException
import xdg_base_dirs


class CalibrolinoException(Exception):
    pass


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
            raise CalibrolinoException(
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
            file_path=self._get_file_path(book_row, file_data)
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
                    authors=metadata['authors'].get(book_id, []),
                    uuid=book_row['uuid'],
                    file_path=file_path,
                    publishers=metadata['publishers'].get(book_id, []),
                    series_index=book_row['series_index'],
                    serie_name=serie_name,
                    tags=metadata['tags'].get(book_id, []),
                    status=status,
                    isbn=book_row['isbn'],
                    pubdate=book_row['pubdate'],
                    languages=metadata['languages'].get(book_id, []),
                    cover_path=cover_path,
                    has_cover=book_row['has_cover'],
                    )
            self._books.append(book)

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


def get_serie_title(title, serie_index, serie_name):
    new_title = f'{serie_name}: {serie_index} - {title}'
    return new_title


class TolinoCloud(object):

    """Docstring for TolinoCloud. """

    def __init__(self, partner, username, password):
        """
        create instance of pytolino.Client
        :partner: str: address of tolino cloud partner
        :username: str
        :password: str
        """

        self._username = username
        self._password = password
        self._client = Client(server_name=partner)

    def get_uploaded_books(self):
        """connect to the cloud and get the books that where already uploaded
        :returns: dict of uploaded books (uuid: books_id)

        """
        return dict()

    def upload_books(self, books):
        """upload to the cloud the selected books

        :books: list of books (dict with metada and path to the file)

        """
        try:
            self._client.login(self._username, self._password)
            self._client.register()
        except PytolinoException:
            print('fail to login')
        else:
            for book in books:
                title = book['title']
                print(f'uploading {title}')
                file_path = book['file_path']
                try:
                    book_id = self._client.upload(file_path)
                    self._add_to_collection(book, book_id)
                    self._upload_cover(book, book_id)
                    self._upload_meta(book, book_id)
                except PytolinoException:
                    print('failed in upload!')


            self._client.unregister()
            self._client.logout()

    def _add_to_collection(self, book, book_id):
        """
        private methode to add to collection

        """
        tags = book['tags']
        for tag in tags:
            self._client.add_to_collection(book_id, tag)
        status = book['status']
        if status is not None:
            self._client.add_to_collection(book_id, status)


    def upload_metadata(self, book, book_id):
        """upload the metadata and cover of a book,
        :book: dict with title, file path an metadata of the book
        :book_id: ref on the cloud pointing to the book"""

        title = book['title']
        print(f'uploading {title} on id={book_id}')

        try:
            self._client.login(self._username, self._password)
            self._client.register()
        except PytolinoException:
            print('fail to login')
        else:
            try:
                self._add_to_collection(book, book_id)
                self._upload_cover(book, book_id)
                self._upload_meta(book, book_id)
            except:
                print('fail to upload')
            finally:
                self._client.unregister()
                self._client.logout()

    def _upload_cover(self, book, book_id):
        """private method to upload the cover


        """
        if book['has_cover']:
            cover_path = book['cover_path']
            self._client.add_cover(book_id, cover_path)

    def _upload_meta(self, book, book_id):
        """private method that upload the metadata

        """
        title = book['title']
        serie_name = book['serie_name']
        if serie_name is not None:
            series_index = book['series_index']
            title = get_serie_title(title, series_index, serie_name)
        metadata = dict(
                title=title,
                isbn=book['isbn'],
                language=book['languages'][0],
                publisher=', '.join(book['publishers']),
                issued=book['pubdate'],
                author=', '.join(book['authors']),
                )
        self._client.upload_metadata(book_id, **metadata)


if __name__ == '__main__':
    calibre_db = CalibreDBReader()
    books = calibre_db.read_db()
    for book in books:
        print('==========')
        for key, value in book.items():
            print(f'{key}: {value}')
            print(type(value))
