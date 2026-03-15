from abc import ABCMeta, abstractmethod, abstractproperty


class GUI(metaclass=ABCMeta):

    """GUI interface for calibrolino"""

    @abstractproperty
    def controller(self) -> type:
        """controller to be set after init"""
        pass

    @abstractmethod
    def __init__(self):
        """gui interface. controller must be set after init """
        pass
