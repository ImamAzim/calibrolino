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
        controller = CalibrolinoController()
        table: BaseTable = Table(self._gui)
        self._gui.table = table
        self._gui.place_card_on_table

    def start(self):
        """start the pycard app

        """
        self._gui.run()


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
    view = CalibrolinoShellView()
    view.start()
