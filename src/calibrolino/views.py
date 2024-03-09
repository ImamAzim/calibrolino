import getpass
from varboxes import VarBox


from pytolino.tolino_cloud import Client, PytolinoException, PARTNERS


from calibrolino.models import CalibreDBReader, CalibrolinoException, TolinoCloud


class CalibrolinoShellView(object):

    """view in shell with a menu to run calibrolino"""

    _welcome_msg = 'welcome to the calibrolino menu'

    def __init__(self):
        self._menu = {
                '1': dict(
                    display='change credentials',
                    method=self._change_credentials,
                    ),
                # '2': dict(
                    # display='connect',
                    # method=self._connect,
                    # ),
                '2': dict(
                    display='upload all the calibre library',
                    method=self._upload_all,
                    ),
                '3': dict(
                    display='upload only one book',
                    method=self._upload_one,
                    ),
                '4': dict(
                    display='show all my books',
                    method=self._print_books,
                    ),
                'q': dict(
                    display='quit',
                    method=self._quit,
                    ),
                }
        self._running = True
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
        if self._calibre_db is not None:
            self._read_db()
        else:
            print('please initiate the calibre db reader first')

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
        print(self._welcome_msg)
        while self._running:
            self._print_menu()
            print(
                    f'I found {len(self._books)} books in your calibre library',
                    )
            choice = input('please select:\n')
            try:
                self._menu[choice]['method']()
            except KeyError:
                print('please select a valid option')
            print('===')

    def _print_menu(self):
        for key, element in self._menu.items():
            print(key, element['display'])

    def _change_credentials(self):
        """
        change the credentials to connect and
        optionnally save them for next time

        """
        for i, partner in enumerate(PARTNERS):
            print(f'{i}: {partner}')
        id_partner = input('please enter the number of the tolino partner you want:')
        try:
            i = int(id_partner)
        except ValueError:
            print('failed! you must enter a valid number partner number')
        else:
            try:
                user_partner = PARTNERS[i]
            except IndexError:
                print('failed! you must enter a valid number partner number')
            else:
                self._credentials.server_name = user_partner
                username = input('username: ')
                self._credentials.username = username
                password = getpass.getpass()
                self._credentials.password = password
                try:
                    self._tolino_cloud = TolinoCloud(
                            self._credentials.server_name,
                            self._credentials.username,
                            self._credentials.password,
                            )
                except PytolinoException:
                    print('failed to use these credentials')
                    self._tolino_cloud = None
                print('warning! your credentials are saved on the disk!',
                        'if you wish to delete them, you can change them again',
                        'and put empty entry')


    def _connect(self):
        """connect to the cloud and get inventory of books
        :returns: TODO

        """
        pass


    def _upload_all(self):
        """upload the whole library

        """
        if self._tolino_cloud is not None:
            uploaded_books = self._tolino_cloud.get_uploaded_books()
            books_to_upload = list()
            for book in self._books:
                if book['uuid'] not in uploaded_books:
                    books_to_upload.append(book)
            print(f'uploading {len(books_to_upload)} books...')
            self._tolino_cloud.upload_books(books_to_upload)
        else:
            print('please enter first your credentials in the main menu')

    def _upload_one(self):
        """upload only one book (for a test)

        """

        for book_index, book in enumerate(self._books):
            print(f'{book_index}: {book['title']}')
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
                    if book_to_upload['uuid'] not in uploaded_books:
                        books_to_upload = list(book_to_upload)
                        self._tolino_cloud.upload_books(books_to_upload)
                    else:
                        print(
                                'the book you chose is already on the cloud',
                                'I will only upload the metadata',
                                )
                        book_id = uploaded_books[book_to_upload['uuid']]
                        self._tolino_cloud.upload_metadata(book_to_upload, book_id)
                else:
                    print('please enter first your credentials in the main menu')

    def _print_books(self):
        for book in self._books:
            print('==========')
            for key, value in book.items():
                print(f'{key}: {value}')

    def _quit(self):
        """
        quit

        """
        print('goodbye')
        self._running = False


if __name__ == '__main__':
    view = CalibrolinoShellView()
    view.start()
    pass
