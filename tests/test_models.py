#!/usr/bin/env python


"""
test all the tools in...
"""

import os
import unittest


from calibrolino.models import CalibreDBReader, get_serie_title


class TestCalibreDBReader(unittest.TestCase):

    """all test concerning CalibreDBReader. """

    @classmethod
    def setUpClass(cls):
        cls.calibre_db_reader = CalibreDBReader()

    def test_init(self):
        CalibreDBReader()


    def test_read_db(self):
        books = self.calibre_db_reader.read_db()
        self.assertGreater(len(books), 0)
        expected_keys = {
                'title',
                'authors',
                'uuid',
                'file_path',
                'publishers',
                'series_index',
                'serie_name',
                'tags',
                'status',
                'isbn',
                'pubdate',
                'languages',
                'cover_path',
                'has_cover',
                }
        for book in books:
            self.assertLessEqual(expected_keys, book.keys())

def test_serie_title():
    title = 'mytitle'
    serie_name = 'myserie'
    serie_index = '42'
    new_title = get_serie_title(title, serie_index, serie_name)
    self.assertIsInstance(new_title, str)
    self.assertIn(title, new_title)
    self.assertIn(serie_name, new_title)
    self.assertIn(serie_index, new_title)


""" script tests """


if __name__ == '__main__':
    print('ok')
    calibre_db_reader = CalibreDBReader()
    books = calibre_db_reader.read_db()
    book = books[0]
    has_cover = book['has_cover']
    print(has_cover, type(has_cover))
    if has_cover:
        print('has a cover!')
    def test_serie_title(self):
        title = 'mytitle'
        serie_name = 'myserie'
        serie_index = '42'
        new_title = self.calibre_db_reader.get_serie_title(title, serie_index, serie_name)
        self.assertIsInstance(new_title, str)
        self.assertIn(title, new_title)
        self.assertIn(serie_name, new_title)
        self.assertIn(serie_index, new_title)
