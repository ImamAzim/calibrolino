import logging
import argparse


from calibrolino.apps import CalibrolinoShellApp


def start_calibrolino():
    parser = argparse.ArgumentParser(
            prog='calibrolino',
            description='sync calibre library to mytolino',
            )

    parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='increase verboxity',
            )

    parser.add_argument(
            '-t',
            '--textmode',
            action='store_true',
            help='use text mode (no GUI)',
            )

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.textmode:
        app = CalibrolinoShellApp()
    else:
        print('TODO: lauch GUI')
    app.start()
