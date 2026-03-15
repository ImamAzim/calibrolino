import logging
import argparse


from calibrolino.views import CalibrolinoShellView
from calibrolino.controllers import CalibrolinoController
from calibrolino.interfaces import View, Controller


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


def start_calibrolino_shell():
    parser = argparse.ArgumentParser(
            prog='calibrolino',
            description='sync calibre library to mytolino',
            )
    parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            )
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    app = CalibrolinoShellApp()
    app.start()
