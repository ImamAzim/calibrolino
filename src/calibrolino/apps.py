from calibrolino.views import CalibrolinoShellView
from calibrolino.gui_views import CalibrolinoGUIView
from calibrolino.controllers import CalibrolinoController


class CalibrolinoShellApp(object):

    """calibrolino app in a shell"""

    def __init__(self):
        """init mvc model """
        self._view = CalibrolinoShellView()
        controller = CalibrolinoController(self._view)
        self._view.controller = controller

    def start(self):
        """start calibrolino

        """
        self._view.start()


class CalibrolinoTkinterApp(object):

    """calibrolino app in tkinter GUI"""

    def __init__(self):
        """init mvc model """
        self._view = CalibrolinoGUIView()
        controller = CalibrolinoController(self._view)
        self._view.controller = controller

    def start(self):
        """start calibrolino

        """
        self._view.start()
