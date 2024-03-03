#!/usr/bin/env python


"""
test all the tools in...
"""

import os
import unittest


from calibrolino import CalibreDBReader


class TestCalibreDBReader(unittest.TestCase):

    """all test concerning CalibreDBReader. """

    @classmethod
    def setUpClass(cls):
        cls.calibre_db_reader = CalibreDBReader()

    def test_init(self):
        CalibreDBReader()

    def test_serie_title(self):
        title = 'mytitle'
        serie_name = 'myserie'
        serie_index = '42'
        new_title = self.calibre_db_reader.get_serie_title(title, serie_index, serie_name)
        self.assertIsInstance(new_title, str)
        self.assertIn(title, new_title)
        self.assertIn(serie_name, new_title)
        self.assertIn(serie_index, new_title)

    def test_read_db(self):
        books = self.calibre_db_reader.read_db()
        self.assertGreater(len(books), 0)
        expected_keys = {
                'title',
                'authors',
                'uuid',
                'file_path',
                'publisher',
                'series_index',
                'serie_name',
                'collection',
                'status',
                'isbn',
                'pubdate',
                'language',
                'cover_path',
                }
        for book in books:
            self.assertLess(expected_keys, book.keys())


""" script tests """


if __name__ == '__main__':
    pass
