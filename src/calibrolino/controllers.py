from varboxes import VarBox
from pytolino.tolino_cloud import PARTNERS
from pandas import DataFrame


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
        except CalibrolinoException as e:
            self._view.showerror(e)
            self._view.showerror('could not use the credentials. bad format?')
            return False
        else:
            self._tolino_cloud = tc
            return True

    @property
    def partners(self) -> list:
        return list(PARTNERS)

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
            msg = (
                    'credentials are saved on the disk. '
                    'if you wish to delete them, you can do it '
                    'in the menu')
            self._view.showinfo(msg)

    @credentials.deleter
    def credentials(self):
        if hasattr(self._varbox, 'partner'):
            delattr(self._varbox, 'partner')
        if hasattr(self._varbox, 'username'):
            delattr(self._varbox, 'username')
        if hasattr(self._varbox, 'password'):
            delattr(self._varbox, 'password')
        self._varbox.info = 'this attr has been set to delete the cred'
        self._tolino_cloud = None

    @property
    def local_books(self) -> dict[dict]:
        return self._calibre_db.books

    def pull(self):

        self._read_db()
        local_lib = self.local_books
        online_lib = self.get_online_books()
        synced_books = {
                key: value for key, value
                in local_lib.items() if key in online_lib}

        if not hasattr(self._varbox, 'revision'):
            answer = self._view.askokcancel(
                    'there are no local sync data. I will create '
                    'an empty one and delete all local tags')
            if not answer:
                return
            else:
                answer = self._view.askyesno(
                        'delete all local tags for books that are also'
                        ' online. are you sure?')
                if not answer:
                    return
                else:
                    self._calibre_db.reset_all_metadata(synced_books)
                    self._varbox.revision = 'needToPullData'
                    self._varbox.patches = dict()

        local_revision = self._varbox.revision
        local_patches = self._varbox.patches
        try:
            x1, x2 = self._tolino_cloud.get_sync_data()
            online_revision, online_patches = x1, x2
        except CalibrolinoException as e:
            self._view.showerror(e)
            self._view.showerror('could not get online sync data')
        else:
            if not online_revision == local_revision:
                for patch_rev, patch in online_patches.items():
                    if patch_rev not in local_patches:
                        ebook_id = self._tolino_cloud.get_ebook_id(patch)
                        if ebook_id in online_lib.values():
                            book_title = [
                                    key
                                    for key, value in online_lib.items()
                                    if value==ebook_id][0]
                        else:
                            print('ebook id no in online lib')
                            print(patch)
                print(online_lib)
                        # self._calibre_db.apply_patch(patch, book_title)

    def get_online_books(self) -> dict:
        online_books = dict()
        if self._tolino_cloud is not None:
            try:
                ob = self._tolino_cloud.get_uploaded_books()
            except CalibrolinoException as e:
                self._view.showerror(e)
                self._view.showerror('could not get online books inv')
            else:
                online_books = ob
        else:
            msg = 'please enter first your credentials in the main menu'
            self._view.showinfo(msg)
        return online_books

    def sync_upload(self) -> None:
        local_books = self.local_books
        online_books = self.get_online_books()
        if online_books is not None:
            books_to_upload = list()
            for full_title, book in local_books.items():
                if full_title not in online_books:
                    books_to_upload.append(book)
            msg = f'I will upload {len(books_to_upload)} books'
            answer = self._view.askokcancel(msg)
            if answer:
                self._tolino_cloud.upload_books(books_to_upload)
                self._view.showinfo('done')

    def upload_book(self, book_title: str):
        try:
            book = self.local_books[book_title]
        except KeyError:
            self._view.showerror(
                    'no book with this title is present in the local library')
        else:
            online_books = self.get_online_books()
            if online_books is not None:
                if book['full_title'] not in online_books:
                    books_to_upload = [book]
                    try:
                        self._tolino_cloud.upload_books(books_to_upload)
                    except CalibrolinoException as e:
                        self._view.showerror(e)
                    else:
                        msg = f'{book_title} has been uploaded'
                        self._view.showinfo(msg)
                else:
                    msg = (
                            'the book you chose is already on the cloud '
                            'I will only upload the metadata')
                    self._view.showinfo(msg)
                    book_id = online_books[book['full_title']]
                    try:
                        self._tolino_cloud.upload_metadata(book, book_id)
                    except CalibrolinoException as e:
                        self._view.showerror(e)
                    else:
                        msg = f'metadata of {book_title} have been uploaded'
                        self._view.showinfo(msg)

    def delete_book(self, book_title: str):
        msg = f'delete {book_title} from the online library. Are you sure?'
        answer = self._view.askyesno(msg)
        if answer:
            online_books = self.get_online_books()
            if online_books is not None:
                try:
                    online_books[book_title]
                except KeyError:
                    self._view.showerror(
                            'no book with this title is present on the cloud')
                else:
                    book_id = online_books[book_title]
                    try:
                        self._tolino_cloud.delete_book(book_id)
                    except CalibrolinoException as e:
                        self._view.showerror(e)
                    else:
                        msg = f'{book_title} has been deleted'
                        self._view.showinfo(msg)

    def _read_db(self):
        """read the calibre library and get books

        """
        try:
            self._calibre_db.read_db()
        except CalibrolinoException:
            self._view.showerror('failed to read the calibre db')

    def get_full_library(self, include_online: bool) -> DataFrame:
        self._read_db()
        local_lib = self.local_books
        if include_online:
            online_lib = self.get_online_books()
        else:
            online_lib = dict()
        local_titles = local_lib.keys()
        online_titles = online_lib.keys()
        all_titles = list(local_titles | online_titles)
        df = DataFrame(dict(local=False, online=False), all_titles)
        for title in local_titles:
            df.at[title, 'local'] = True
        for title in online_lib:
            df.at[title, 'online'] = True
        return df
