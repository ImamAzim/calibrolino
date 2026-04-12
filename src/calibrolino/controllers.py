from varboxes import VarBox
from pytolino.tolino_cloud import PARTNERS
from pandas import DataFrame
import logging


from calibrolino.interfaces import Controller, View
from calibrolino.models import CalibreDBReader
from calibrolino.models import CalibrolinoException
from calibrolino.models import PatchAlreadyAppliedError
from calibrolino.models import PatchAlreadyUnappliedError
from calibrolino.models import TolinoCloud, ONLINE_ID
from calibrolino.models import TolinoCloudException
from calibrolino.interfaces import ControllerException


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
                'in the menu'
            )
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

    def reset_local_library(self):
        self._calibre_db.read_db()
        local_lib = self.local_books
        online_lib = self.get_online_books()
        local_books_to_sync = dict()
        for book_id, book in local_lib.items():
            title = book['full_title']
            if title in online_lib.values():
                for online_id, online_title in online_lib.items():
                    if title == online_title:
                        local_books_to_sync[book_id] = online_id
                        online_lib.pop(online_id)
                        break
        n = len(local_books_to_sync)
        answer = self._view.askyesno(
            'delete all local tags for books that are also'
            f' online ({n} books). are you sure?'
        )
        if not answer:
            return
        else:
            self._calibre_db.reset_all_metadata(local_books_to_sync)

            revision = 'needToPullData'
            self._varbox.revision = revision
            self._varbox.patches = dict()

    def pull(self, force=False):
        """
        force: if True, it will look at new patches even if revision
        number did not change. That is usefull if a book has been
        added to the library
        """

        if not hasattr(self._varbox, 'revision'):
            answer = self._view.askokcancel(
                'there are no local sync data. I will create '
                'an empty one and delete all local tags'
            )
            if not answer:
                return
            else:
                self.reset_local_library()

        self._read_db()

        local_revision = self._varbox.revision
        local_patches = self._varbox.patches
        try:
            x1, x2 = self._tolino_cloud.get_sync_data()
            online_revision, online_patches = x1, x2
        except CalibrolinoException as e:
            self._view.showerror(e)
            self._view.showerror('could not get online sync data')
        else:
            if not online_revision == local_revision or force:
                revision_applied = True
                added = 0
                for patch_rev, patch in online_patches.items():
                    if patch_rev not in local_patches:
                        online_id = self._tolino_cloud.get_ebook_id(patch)
                        if online_id in self._calibre_db.online_books:
                            book_id = self._calibre_db.online_books[online_id]
                            try:
                                self._calibre_db.apply_patch(patch, book_id)
                            except NotImplementedError as e:
                                revision_applied = False
                                self._view.showerror(e)
                            except PatchAlreadyAppliedError as e:
                                logging.warning(e)
                                logging.warning('patch were already applied')
                                local_patches[patch_rev] = patch
                            else:
                                local_patches[patch_rev] = patch
                                added += 1
                suppressed = 0
                patch_rev_to_delete = list()
                for patch_rev, patch in local_patches.items():
                    if patch_rev not in online_patches:
                        online_id = self._tolino_cloud.get_ebook_id(patch)
                        if online_id in self._calibre_db.online_books:
                            book_id = self._calibre_db.online_books[online_id]
                            try:
                                self._calibre_db.unapply_patch(patch, book_id)
                            except NotImplementedError as e:
                                revision_applied = False
                                self._view.showerror(e)
                            except PatchAlreadyUnappliedError as e:
                                logging.warning(e)
                                logging.warning('patch were already unapplied')
                                patch_rev_to_delete.append(patch_rev)
                            else:
                                patch_rev_to_delete.append(patch_rev)
                                suppressed += 1
                for patch_rev in patch_rev_to_delete:
                    del local_patches[patch_rev]
                if revision_applied:
                    self._calibre_db.commit()
                    self._varbox.patches = local_patches
                    self._varbox.revision = online_revision
                    self._view.showinfo(
                        f'pull sync finished. {added} patch added, '
                        f'{suppressed} patch removed'
                    )
                else:
                    self._view.showinfo(
                        'revision not applied because some patches'
                        ' are not implemented'
                    )
            else:
                self._view.showinfo('local books already synced')

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
            for local_id, book in local_books.items():
                online_id = book.get('online_id')
                if online_id not in online_books:
                    books_to_upload.append(local_id)
            msg = f'I will upload {len(books_to_upload)} books'
            answer = self._view.askokcancel(msg)
            if answer:
                for book_id in books_to_upload:
                    self.upload_book(book_id)

    def download_book(self, online_id):
        self._read_db()
        if online_id in self._calibre_db.online_books:
            msg = 'book is already in the local lib. use PULL to sync data'
            raise ControllerException(msg)
        online_books = self.get_online_books()
        try:
            online_books[online_id]
        except KeyError:
            self._view.showerror('book not found on the cloud')
        else:
            try:
                res = self._tolino_cloud.download_book(online_id)
                book_path, cover_path, metadata = res
            except TolinoCloudException as e:
                self._view.showerror(e)
            else:
                metadata_nonone = {
                    key: value
                    for key, value in metadata.items()
                    if value is not None
                }
                metadata_nonone.pop('publisher')
                metadata_nonone.pop('issued')
                try:
                    book_id = self._calibre_db.add_book(
                        book_path, **metadata_nonone
                    )
                except CalibrolinoException as e:
                    self._view.showerror(e)
                else:
                    self._calibre_db.add_online_id(book_id, online_id)
                    self._calibre_db.commit()
                    self.pull(force=True)

    def download_all(self):
        self.local_books
        online_books = self.get_online_books()
        books_to_download = list()
        for online_id in online_books:
            if online_id not in self._calibre_db.online_books:
                books_to_download.append(online_id)
        msg = f'I will download {len(books_to_download)} books'
        answer = self._view.askokcancel(msg)
        if answer:
            for online_id in books_to_download:
                self.download_book(online_id)

    def delete_book_locally(self, book_id):
        self._read_db()
        if book_id not in self.local_books:
            self._view.showerror('this book is not present in the library')
        else:
            book = self.local_books[book_id]
            book_title = book['title']
            msg = f'delete {book_title} from calibre. Are you sure?'
            answer = self._view.askyesno(msg)
            if answer:
                try:
                    self._calibre_db.delete_book(book_id)
                except CalibrolinoException as e:
                    self._view.showerror(e)
                except NotImplementedError as e:
                    self._view.showerror('not implemented')

    def upload_book(self, local_id: int):
        try:
            book = self.local_books[local_id]
        except KeyError:
            self._view.showerror(
                'this book is not present in the local library'
            )
        else:
            online_id = book.get('online_id')
            online_lib = self.get_online_books()
            if online_id not in online_lib:
                try:
                    online_id = self._tolino_cloud.upload_book(book)
                except CalibrolinoException as e:
                    self._view.showerror(e)
                else:
                    if book.get('online_id'):
                        self._calibre_db.rm_online_id(local_id)
                    self._calibre_db.add_online_id(local_id, online_id)
                    self._calibre_db.commit()
                    try:
                        res = self._tolino_cloud.upload_all_tags_of_book(
                            book, online_id
                        )
                        revision, patches = res
                    except CalibrolinoException as e:
                        self._view.showerror(e)
                    else:
                        if revision:
                            saved_patches = self._varbox.patches
                            self._varbox.revision = revision
                            saved_patches.update(patches)
                            self._varbox.save()
            else:
                msg = (
                    'book already present on the cloud. use PUSH '
                    'function (not implemented) to update tags and '
                    'others data'
                )
                self._view.showinfo(msg)

    def delete_book(self, online_id: str):
        online_books = self.get_online_books()
        if online_id not in online_books:
            self._view.showerror('this book is not present on the cloud')
        else:
            book_title = online_books[online_id]
            msg = f'delete {book_title} from the online library. Are you sure?'
            answer = self._view.askyesno(msg)
            if answer:
                try:
                    self._tolino_cloud.delete_book(online_id)
                except CalibrolinoException as e:
                    self._view.showerror(e)
                else:
                    local_id = self._calibre_db.online_books.get(online_id)
                    if local_id:
                        self._calibre_db.rm_online_id(local_id)
                        self._calibre_db.commit()
                    msg = f'{book_title} has been deleted'
                    self._view.showinfo(msg)

    def _read_db(self):
        """read the calibre library and get books"""
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
        df = DataFrame(
            dict(title='', local_id=0, online_id=''), local_lib.keys()
        )
        for book_id, book in local_lib.items():
            df.at[book_id, 'title'] = book['full_title']
            df.at[book_id, 'local_id'] = book_id
            online_id = book.get(ONLINE_ID)
            if online_id in online_lib:
                df.at[book_id, 'online_id'] = online_id
        for online_id, title in online_lib.items():
            if online_id not in self._calibre_db.online_books:
                df.loc[online_id] = {
                    'title': title,
                    'local_id': 0,
                    'online_id': online_id,
                }
        return df
