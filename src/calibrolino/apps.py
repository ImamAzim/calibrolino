from calibrolino.views import CalibrolinoShellView
import logging
import argparse


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
