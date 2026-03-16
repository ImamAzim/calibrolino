import getpass
from pytolino.tolino_cloud import PytolinoException, PARTNERS


from calibrolino.models import TolinoCloud
from calibrolino.interfaces import View, Controller


class CalibrolinoShellView(View):

    """view in shell with a menu to run calibrolino"""

    _welcome_msg = 'welcome to the calibrolino menu'

    @property
    def controller(self) -> Controller:
        return self._controller

    @controller.setter
    def controller(self, value: Controller):
        self._controller = value

    def showinfo(self, msg: str):
        print('info:', msg)

    def showerror(self, msg: str):
        print('error!', msg)

    def __init__(self):
        self._menu = {
                '1': dict(
                    display='change credentials',
                    method=self._change_credentials,
                    ),
                '99': dict(
                    display='show credentials',
                    method=self._show_credentials,
                    ),
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

    def start(self):

        print(self._welcome_msg)
        self._local_books = self.controller.local_books
        while self._running:
            self._print_menu()
            print(
                    f'I found {len(self._local_books)} books in your calibre library',
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

    def _show_credentials(self):
        credentials = self.controller.credentials
        print(credentials)

    def _change_credentials(self):
        """
        change the credentials to connect and
        save them for next time

        """
        partners_list = list(PARTNERS)
        for i, partner in enumerate(partners_list):
            print(f'{i}: {partner}')
        id_partner = input('please enter the number of the tolino partner you want:')
        try:
            i = int(id_partner)
        except ValueError:
            print('failed! you must enter a valid number partner number')
        else:
            try:
                user_partner = partners_list[i]
            except IndexError:
                print('failed! you must enter a valid number partner number')
            else:
                username = input('username: ')
                password = getpass.getpass()
                credentials = dict(partner=user_partner,
                                   username=username,
                                   password=password,)
                self._controller.credentials = credentials

    def _upload_all(self):
        """upload the whole library

        """
        self._local_books = self.controller.local_books
        if self._tolino_cloud is not None:
            uploaded_books = self._tolino_cloud.get_uploaded_books()
            if uploaded_books is not None:
                books_to_upload = list()
                for book in self._local_books:
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

        self._local_books = self.controller.local_books
        for book_index, book in enumerate(self._local_books):
            title = book['title']
            print(f'{book_index}: {title}')
        book_index_choice = input('enter the book number you want to upload:\n')

        try:
            i = int(book_index_choice)
        except ValueError:
            print('failed! you must enter a valid number')
        else:
            try:
                book_to_upload = self._local_books[i]
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
        self._local_books = self.controller.local_books
        for book in self._local_books:
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
