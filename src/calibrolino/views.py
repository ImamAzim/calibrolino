from calibrolino.models import CalibreDBReader, CalibrolinoException


class CalibrolinoShellView(object):

    """view in shell with a menu to run calibrolino"""

    _welcome_msg = 'welcome to the calibrolino menu'

    def __init__(self):
        self._menu = {
                '1': dict(
                    display='change credentials',
                    method=self._change_credentials,
                    ),
                '2': dict(
                    display='connect',
                    method=self._connect,
                    ),
                '3': dict(
                    display='upload all the calibre library',
                    method=self._upload_all,
                    ),
                '4': dict(
                    display='upload only one book',
                    method=self._upload_one,
                    ),
                'q': dict(
                    display='quit',
                    method=self._quit,
                    ),
                }
        self._running = True
        self._calibre_db = None
        self._books = list()
        self._books_to_upload = list()

        self._init_dbreader()
        if self._calibre_db is not None:
            self._read_db()
        else:
            print('please initiate the calibre db reader first')

    def _init_dbreader():
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
                    f'I found {len(self._books)} in your calibre library',
                    f'there are {len(self._books_to_upload)} books that you can upload',
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
        print('enter the new credentials')

    def _connect(self):
        """connect to the cloud and get inventory of books
        :returns: TODO

        """
        pass

    def _upload_all(self):
        """upload the whole library
        :returns: TODO

        """
        pass

    def _upload_one(self):
        """upload only one book (for a test)
        :returns: TODO

        """
        pass

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
