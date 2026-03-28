from abc import ABCMeta, abstractmethod, abstractproperty


from pandas import DataFrame


class Controller(metaclass=ABCMeta):

    """Controller for calibrolino """

    @abstractproperty
    def partners(self) -> dict:
        """list of tolino partner (arg for tolinocloud class)

        """
        pass

    @abstractproperty
    def credentials(self) -> dict:
        """credentials that can be saved and loaded from disk

        """
        pass

    @abstractproperty
    def local_books(self) -> dict:
        """a dict of books present in calibre library, in form of dict
        with metadata. keys are full title"""
        pass

    @abstractmethod
    def get_online_books(self) -> dict:
        """connect to the cloud and get inventory of books
        :returns: [title]: epub_id

        """
        pass

    @abstractmethod
    def sync_upload(self) -> None:
        """upload all local books that are not yet online

        """
        pass

    @abstractmethod
    def upload_book(self, book_title: str):
        """upload the book

        :book_title: should be in the local library

        """
        pass

    @abstractmethod
    def delete_book(self, book_title: str):
        """delete the book from the cloud

        :book_title: should be in the online library

        """
        pass

    @abstractmethod
    def get_full_library(self) -> tuple[DataFrame, dict, dict]:
        """read local db and online cloud to get a library of all books
        :returns: table with title, local (True/False), online (True/False)
        and local and online books

        """
        pass

    @abstractmethod
    def pull(self):
        """fetch sync data from server and apply changes to local lib

        """
        pass


class View(metaclass=ABCMeta):

    """GUI interface for calibrolino"""

    @abstractproperty
    def controller(self) -> type:
        """controller to be set after init"""
        pass

    @abstractmethod
    def __init__(self):
        """gui interface. controller must be set after init """
        pass

    @abstractmethod
    def start(self):
        """start the gui (in a loop)

        :returns: TODO

        """
        pass

    @abstractmethod
    def showinfo(self, msg: str):
        """display a msg, for example from controller

        :msg: message from controller

        """
        pass

    @abstractmethod
    def showerror(self, msg: str):
        """display an error msg, for example from controller

        :msg: message from controller

        """
        pass

    @abstractmethod
    def askokcancel(self, msg: str) -> bool:
        """Ask if operation should proceed. Shows OK and CANCEL.

        :msg: message to be displayed
        :returns: True if the answer is ok and False otherwise.

        """
        pass

    @abstractmethod
    def askyesno(self, msg: str) -> bool:
        """Ask a questions. Shows YES and NO.

        :msg: message to be displayed
        :returns: True if the answer is yes and False otherwise.


        """
        pass
