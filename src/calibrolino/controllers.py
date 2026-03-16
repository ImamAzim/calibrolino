from varboxes import VarBox


from calibrolino.interfaces import Controller, View
from calibrolino.models import CalibreDBReader
from calibrolino.models import CalibrolinoException
from calibrolino.models import TolinoCloud


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

        credentials = self.credentials
        if credentials:
            try:
                tc = TolinoCloud(**credentials)
            except PytolinoException:
                self._tolino_cloud = None
            else:
                self._tolino_cloud = tc
        else:
            self._tolino_cloud = None

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
        self._varbox.partner = value['partner']
        self._varbox.username = value['username']
        self._varbox.password = value['password']

    @property
    def local_books(self) -> list[dict]:
        self._read_db()
        return self._local_books

    def get_online_books(self) -> dict:
        raise NotImplementedError

    def sync_upload(self) -> None:
        raise NotImplementedError

    def upload_book(self, book: dict):
        raise NotImplementedError

    def _read_db(self):
        """read the calibre library and get books

        """
        try:
            local_books = self._calibre_db.read_db()
        except CalibrolinoException:
            self._view.showerror('failed to read the calibre db')
        else:
            self._local_books = local_books
