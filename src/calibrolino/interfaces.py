from abc import ABCMeta, abstractmethod, abstractproperty


class Controller(metaclass=ABCMeta):

    """Controller for calibrolino """

    @abstractproperty
    def credentials(self) -> dict:
        """credentials that can be saved and loaded from disk

        """
        pass

    @abstractproperty
    def local_books(self) -> list[dict]:
        """a list books present in calibre library, in form of dict
        with metadata"""
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
    def upload_book(self, book: dict):
        """upload the book

        :book: contain metadata and path to file

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
