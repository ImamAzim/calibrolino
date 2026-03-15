import getpass
from varboxes import VarBox


from pytolino.tolino_cloud import Client, PytolinoException, PARTNERS


from calibrolino.models import CalibreDBReader, CalibrolinoException
from calibrolino.modely import TolinoCloud


class CalibrolinoGUIView(object):

    """GUI view run calibrolino"""

    _welcome_msg = 'welcome to the calibrolino menu'

    def __init__(self):
        self._calibre_db = None
        self._books = list()
        self._credentials = VarBox('calibrolino')

        if hasattr(self._credentials, 'password'):
            try:
                self._tolino_cloud = TolinoCloud(
                        self._credentials.server_name,
                        self._credentials.username,
                        self._credentials.password,
                        )
            except PytolinoException:
                self._tolino_cloud = None
        else:
            self._tolino_cloud = None

        self._init_dbreader()
        self._read_db()

    def _init_dbreader(self):
        """create an instance of CalibreDBReader"""
        try:
            self._calibre_db = CalibreDBReader()
        except CalibrolinoException:
            print('failed to create an instance of calibre db reader')

    def _read_db(self):
        """read the calibre library and get books

        """
        try:
            self._books = self._calibre_db.read_db()
        except CalibrolinoException:
            print('failed to read the db')

    def start(self):
        pass

    def _change_credentials(self):
        """
        change the credentials to connect and
        optionnally save them for next time

        """
        pass

    def _upload_all(self):
        """upload the whole library

        """
        if self._tolino_cloud is not None:
            uploaded_books = self._tolino_cloud.get_uploaded_books()
            if uploaded_books is not None:
                books_to_upload = list()
                for book in self._books:
                    if book['full_title'] not in uploaded_books:
                        books_to_upload.append(book)
                print(f'uploading {len(books_to_upload)} books...')
                self._tolino_cloud.upload_books(books_to_upload)
            else:
                print('could not get inventory of uploaded books. I will not do anything.')

        else:
            print('please enter first your credentials in the main menu')

    def _upload_one(self):
        """upload only one book (for a test)

        """

        for book_index, book in enumerate(self._books):
            title = book['title']
            print(f'{book_index}: {title}')
        book_index_choice = input('enter the book number you want to upload:\n')

        try:
            i = int(book_index_choice)
        except ValueError:
            print('failed! you must enter a valid number')
        else:
            try:
                book_to_upload = self._books[i]
            except IndexError:
                print('failed! you must enter the book number you want to upload')
            else:
                if self._tolino_cloud is not None:
                    uploaded_books = self._tolino_cloud.get_uploaded_books()
                    if uploaded_books is not None:
                        if book_to_upload['full_title'] not in uploaded_books:
                            books_to_upload = [book_to_upload]
                            self._tolino_cloud.upload_books(books_to_upload)
                        else:
                            print(
                                    'the book you chose is already on the cloud',
                                    'I will only upload the metadata',
                                    )
                            book_id = uploaded_books[book_to_upload['issued']]
                            self._tolino_cloud.upload_metadata(book_to_upload, book_id)
                    else:
                        print('could not get inventory of uploaded books. I will not do anything.')
                else:
                    print('please enter first your credentials in the main menu')

    def _print_books(self):
        for book in self._books:
            print('==========')
            for key, value in book.items():
                print(f'{key}: {value}')


if __name__ == '__main__':
    view = CalibrolinoGUIView()
    view.start()
