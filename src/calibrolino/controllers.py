from varboxes import VarBox


from calibrolino.interfaces import Controller, View
from calibrolino.models import CalibreDBReader
from calibrolino.models import CalibrolinoException
from calibrolino.models import TolinoCloud, TolinoCloudException


class CalibrolinoController(Controller):

    """controller of calibrolino in mvc arch"""

    def __init__(self, view: View):
        Controller.__init__(self)
        self._view = view
        self._varbox = VarBox('calibrolino')
        self._local_books = list()
        try:
            self._calibre_db = CalibreDBReader()
        except CalibrolinoException:
            self._calibre_db = None
            self._view.showerror('could not read calibre library!')

        self._tolino_cloud = None
        credentials = self.credentials
        if credentials:
            self._init_tolino_cloud(credentials)

    def _init_tolino_cloud(self, credentials):
        try:
            tc = TolinoCloud(**credentials)
        except TolinoCloudException as e:
            self._view.showerror(e)
            self._view.showerror('could not use the credentials. bad format?')
            return False
        else:
            self._tolino_cloud = tc
            return True

    @property
    def credentials(self) -> dict:
        try:
            credentials = dict(
                    partner=self._varbox.partner,
                    username=self._varbox.username,
                    password=self._varbox.password,
                    )
        except AttributeError:
            credentials = None
        return credentials

    @credentials.setter
    def credentials(self, value: dict):
        success = self._init_tolino_cloud(value)
        if success:
            self._varbox.partner = value['partner']
            self._varbox.username = value['username']
            self._varbox.password = value['password']
            msg = 'credentials are saved on the disk.'
            'if you wish to delete them, you can change them '
            'again and put empty entry'
            self._view.showinfo(msg)

    @property
    def local_books(self) -> list[dict]:
        self._read_db()
        return self._local_books

    def get_online_books(self) -> dict:
        raise NotImplementedError

    def sync_upload(self) -> None:
        raise NotImplementedError

    def upload_book(self, book: dict):
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
            msg = 'please enter first your credentials in the main menu'
            self._view.showinfo(msg)


    def _read_db(self):
        """read the calibre library and get books

        """
        try:
            local_books = self._calibre_db.read_db()
        except CalibrolinoException:
            self._view.showerror('failed to read the calibre db')
        else:
            self._local_books = local_books
