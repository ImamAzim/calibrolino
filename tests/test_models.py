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

    def test_online_id(self):
        cdb = self.calibre_db_reader
        self.assertTrue(hasattr(cdb, 'online_books'))


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
    print(f'book added: {book_id}')
    search_book_test(calibre_db)
    add_tag_test(calibre_db, book_id)
    rm_tag_test(calibre_db, book_id)
    add_online_id_test(calibre_db, book_id)
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

def add_online_id_test(calibre_db, book_id):
    books = calibre_db.books
    book = books[book_id]
    print(calibre_db.online_books)
    print('online_id', book.get('online_id'))
    try:
        calibre_db.add_online_id(book_id, 'fakeonlineid')
    except CalibrolinoException as e:
        print(e)
    else:
        print('online id added:')
        books = calibre_db.books
        book = books[book_id]
        print('online_id', book.get('online_id'))
        print(calibre_db.online_books)

def rm_online_id_test(calibre_db):
    print('TODO: test rm online id')

def search_book_test(calibre_db):
    print('search book...')
    try:
        book_id = calibre_db.search_book('title', TEST_BOOK_TITLE)
    except CalibreDBReader as e:
        print(e)
    else:
        print('book found!')
        print(book_id)

if __name__ == '__main__':
    calibre_db = CalibreDBReader()
    # add_rm_book_test(calibre_db)
    # full_test()
    # for book in calibre_db.books:
        # print(book)
        # print(book.keys())
    # add_tag_test(calibre_db)
    # rm_tag_test(calibre_db)
    # calibre_db.commit()
