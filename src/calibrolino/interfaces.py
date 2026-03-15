from abc import ABCMeta, abstractmethod, abstractproperty


class Controller(metaclass=ABCMeta):

    """Controller for calibrolino """

    @abstractproperty
    def credentials(self) -> dict:
        """credentials that can be saved and loaded from disk

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
