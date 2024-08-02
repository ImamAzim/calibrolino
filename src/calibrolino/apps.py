from calibrolino.views import CalibrolinoShellView
import logging


def start_calibrolino_shell():
    view = CalibrolinoShellView()
    view.start()

def start_debug_mode():
    logging.basicConfig(level=logging.INFO)
    start_calibrolino_shell()
