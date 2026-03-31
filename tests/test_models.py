import unittest
from pathlib import Path


from calibrolino.models import CalibreDBReader, get_serie_title, CalibrolinoException

TEST_BOOK_TITLE = 'added by calibrolino'
TEST_BOOK_FN = 'minimal-v3.epub'

test_book_fp = Path(__file__).parent / TEST_BOOK_FN



class TestCalibreDBReader(unittest.TestCase):

    """all test concerning CalibreDBReader. """

    @classmethod
    def setUpClass(cls):
        cls.calibre_db_reader = CalibreDBReader()

    def test_init(self):
        CalibreDBReader()

    def test_books(self):
        books = self.calibre_db_reader.books
        self.assertGreater(len(books), 0)
        expected_keys = {
                'title',
                'full_title',
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
                'issued',
                'last_modified',
                'book_id',
                }
        for title, book in books.items():
            for expected_key in expected_keys:
                self.assertIn(expected_key, book)

    def test_serie_title(self):
        title = 'mytitle'
        serie_name = 'myserie'
        serie_index = '42'
        new_title = get_serie_title(title, serie_index, serie_name)
        self.assertIsInstance(new_title, str)
        self.assertIn(title, new_title)
        self.assertIn(serie_name, new_title)
        self.assertIn(serie_index, new_title)


""" script tests """

def add_tag_test(calibre_db, book_id):
    books = calibre_db.books
    book = books[book_id]
    print('tags', book['tags'])
    try:
        calibre_db.add_tag(book_id, 'test')
    except CalibrolinoException as e:
        print(e)
    else:
        print('tag added:')
        books = calibre_db.books
        book = books[book_id]
        print('tags', book['tags'])

def full_test():
    calibre_db = CalibreDBReader()
    book_id = calibre_db.add_book(test_book_fp, title=TEST_BOOK_TITLE)
    add_tag_test(calibre_db, book_id)
    rm_tag_test(calibre_db, book_id)
    calibre_db.commit()
    calibre_db.remove_book(book_id)

def rm_tag_test(calibre_db, book_id):
        try:
            calibre_db.rm_tag(book_id, 'test')
        except CalibrolinoException as e:
            print(e)
        else:
            print('tag removed:')
            books = calibre_db.books
            book = books[book_id]
            print('tags', book['tags'])

def add_rm_book_test(calibre_db):
    book_id = calibre_db.add_book(test_book_fp, title=TEST_BOOK_TITLE)
    print(book_id)
    calibre_db.remove_book(book_id)

if __name__ == '__main__':
    calibre_db = CalibreDBReader()
    # add_rm_book_test(calibre_db)
    full_test()
    # for book in calibre_db.books:
        # print(book)
        # print(book.keys())
    # add_tag_test(calibre_db)
    # rm_tag_test(calibre_db)
    # calibre_db.commit()
