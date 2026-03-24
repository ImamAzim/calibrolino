#!/usr/bin/env python

import os
import json
import sqlite3
import sys
import datetime
from pathlib import Path


from pytolino.tolino_cloud import Client, PytolinoException
import xdg_base_dirs


class CalibrolinoException(Exception):
    pass


class TolinoCloudException(Exception):
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

    _accepted_formats = {'EPUB'}
    _column_status_name = 'status'

    @property
    def books(self) -> dict:
        """a dictionnory of books (keys are the titles). each book dict
        contains metadata of the books and file path to book"""
        return self._books

    def __init__(self):
        """
        finds the calibre db and connect to it
        """

        self._get_calibre_db()
        self._load_db()
        self.read_db()

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

    def add_tag(self, book, tag_name):
        """TODO: Docstring for add_tag.

        :arg1: TODO
        :returns: TODO

        """
        if tag_name in self.books[book['title']]['tags']:
            raise CalibrolinoException('tag is already on this book')
        book_id = book['book_id']
        if tag_name not in self._tags:
            tag_id = self._create_tag(tag_name)
        tag_id = self._tags[tag_name]
        table_name = 'books_tags_link'
        sql = f"""
        INSERT INTO {table_name} (book, tag)
        VALUES ({book_id}, {tag_id});
        """
        res = self._con.execute(sql)
        book = self._books[book['title']]
        book['tags'].append(tag_name)

    def commit(self):
        """save changes to the db

        """
        self._con.commit()

    def rm_tag(self, book, tag_name):
        """TODO: Docstring for add_tag.

        :arg1: TODO
        :returns: TODO

        """
        if tag_name not in self.books[book['title']]['tags']:
            raise CalibrolinoException('already such tag in this book')
        book_id = book['book_id']
        tag_id = self._tags[tag_name]
        table_name = 'books_tags_link'
        sql = f"""
        DELETE FROM {table_name}
        WHERE book={book_id} AND tag={tag_id};
        """
        res = self._con.execute(sql)

        table_name = 'books_tags_link'
        sql = f"""
        SELECT * FROM {table_name}
        WHERE tag={tag_id};
        """
        res = self._con.execute(sql)
        if res.fetchone() is None:
            table_name = 'tags'
            sql = f"""
            DELETE FROM {table_name}
            WHERE name='{tag_name}';
            """
            res = self._con.execute(sql)
        self.read_db()

    def _create_tag(self, tag_name):
        table_name = 'tags'
        sql = f"""
        INSERT INTO {table_name} (name)
        VALUES ('{tag_name}');
        """
        res = self._con.execute(sql)
        self._get_all_tables()
        self._create_tags_dict()

    def _get_all_tables(self):

        self._tables = dict()

        for table_name in self._calibre_db_table:
            self._tables[table_name] = self._get_table(table_name)
        try:
            table_name = self._add_custom_column_table(self._column_status_name)
        except CalibrolinoException:
            self._status_is_defined = False
        else:
            self._status_is_defined = True
            self._status_table_name = table_name

    def _add_custom_column_table(self, column_name):

        custom_column_id = None
        for custom_column in self._tables['custom_columns']:
            if custom_column['name'] == column_name:
                custom_column_id = custom_column['id']
        if custom_column_id is None:
            raise CalibrolinoException
        table_name = f'custom_column_{custom_column_id}'
        table_names = table_name, f'books_{table_name}_link'
        for table_name in table_names:
            self._tables[table_name] = self._get_table(table_name)
        return table_name

    def _create_tags_dict(self):
        self._tags = dict()
        metadata_tables = self._tables['tags']
        for row in metadata_tables:
            self._tags[row['name']] = row['id']

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
                    (self._status_table_name, 'value', 'value')
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

        self._books = dict()

        for book_row in self._tables['books']:
            book_id = book_row['id']
            file_data = files_data[book_id]
            book_format = file_data['format']
            if book_format in self._accepted_formats:
                file_path=self._get_file_path(book_row, file_data)
                title = book_row['title']
                serie_name=metadata['series'].get(book_id)
                series_index=book_row['series_index']
                if serie_name is not None:
                    serie_name = serie_name[0]
                    full_title = get_serie_title(title, series_index, serie_name)
                else:
                    full_title = title
                if self._status_is_defined:
                    status = metadata[self._status_table_name].get(book_id)
                else:
                    status = None
                cover_path = self._get_cover_path(book_row, file_data)

                issued_datetime = datetime.datetime.fromisoformat(book_row['pubdate'])
                issued_timestamps = int(issued_datetime.timestamp())

                book = dict(
                        title=title,
                        full_title=full_title,
                        authors=metadata['authors'].get(book_id, []),
                        uuid=book_row['uuid'],
                        file_path=file_path,
                        publishers=metadata['publishers'].get(book_id, []),
                        series_index=series_index,
                        serie_name=serie_name,
                        tags=metadata['tags'].get(book_id, []),
                        status=status,
                        isbn=book_row['isbn'],
                        pubdate=book_row['pubdate'],
                        issued=issued_timestamps,
                        languages=metadata['languages'].get(book_id, []),
                        cover_path=cover_path,
                        has_cover=book_row['has_cover'],
                        last_modified=book_row['last_modified'],
                        book_id=book_id,
                        )
                self._books[full_title] = book

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

    def read_db(self):
        """
        load the calibre db and create a list of the books with metadata

        """

        self._get_all_tables()
        self._create_books_dict()
        self._create_tags_dict()


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

        self._password = password
        try:
            self._client = Client(server_name=partner, username=username)
        except PytolinoException as e:
            raise TolinoCloudException(str(e))

    def get_uploaded_books(self):
        """connect to the cloud and get the books that where already uploaded
        :returns: dict of uploaded books (full_title: books_id)

        """
        try:
            self._client.login(self._password)
        except PytolinoException as e:
            raise CalibrolinoException(str(e))
        else:
            try:
                inventory = self._client.get_inventory()
                uploaded_books = dict()
                for book in inventory:
                    full_title = book['epubMetaData']['title']
                    book_id = book['publicationId']
                    uploaded_books[full_title] = book_id
                return uploaded_books
            except PytolinoException as e:
                raise TolinoCloudException(str(e))

    def upload_books(self, books):
        """upload to the cloud the selected books

        :books: list of books (dict with metada and path to the file)

        """
        try:
            self._client.login(self._password)
        except PytolinoException as e:
            raise CalibrolinoException(str(e))
        else:
            for book in books:
                title = book['title']
                print(f'uploading {title}')
                file_path = book['file_path']
                try:
                    book_id = self._client.upload(file_path)
                except PytolinoException as e:
                    raise CalibrolinoException(str(e))
                else:
                    try:
                        self._add_to_collection(book, book_id)
                    except PytolinoException as e:
                        raise CalibrolinoException(str(e))
                    try:
                        self._upload_cover(book, book_id)
                    except PytolinoException as e:
                        raise CalibrolinoException(str(e))
                    try:
                        self._upload_meta(book, book_id)
                    except PytolinoException as e:
                        raise CalibrolinoException(str(e))
                    print('book uploaded')

    def _add_to_collection(self, book, book_id):
        """
        private methode to add to collection

        """
        tags = book['tags']
        for tag in tags:
            self._client.add_to_collection(book_id, tag)
        statuses = book['status']
        if statuses is not None:
            for status in statuses:
                self._client.add_to_collection(book_id, status)


    def upload_metadata(self, book, book_id):
        """upload the metadata and cover of a book,
        :book: dict with title, file path an metadata of the book
        :book_id: ref on the cloud pointing to the book"""

        title = book['title']
        print(f'uploading {title} on id={book_id}')

        try:
            self._client.login(self._password)
        except PytolinoException as e:
            raise CalibrolinoException(str(e))
        else:
            try:
                self._add_to_collection(book, book_id)
                self._upload_cover(book, book_id)
                self._upload_meta(book, book_id)
            except PytolinoException as e:
                raise CalibrolinoException(str(e))

    def delete_book(self, book_id):
        """delete book from online lib
        :book_id: ref on the cloud pointing to the book"""

        try:
            self._client.login(self._password)
        except PytolinoException as e:
            raise CalibrolinoException(str(e))
        else:
            try:
                self._client.delete_ebook(book_id)
            except PytolinoException as e:
                raise CalibrolinoException(str(e))

    def _upload_cover(self, book, book_id):
        """private method to upload the cover


        """
        if book['has_cover']:
            cover_path = book['cover_path']
            self._client.add_cover(book_id, cover_path)

    def _upload_meta(self, book, book_id):
        """private method that upload the metadata

        """
        full_title = book['full_title']
        language = book['languages'][0] if book['languages'] else ''
        metadata = dict(
                title=full_title,
                isbn=book['isbn'],
                language=language,
                publisher=', '.join(book['publishers']),
                issued=book['issued'],
                author=', '.join(book['authors']),
                )
        self._client.upload_metadata(book_id, **metadata)


if __name__ == '__main__':
    pass

    # for title, book in books.items():
        # print('==========')
        # print(title)
        # for key, value in book.items():
            # print(f'{key}: {value}')
    # print(calibre_db._tables)

