class CalibrolinoShellView(object):

    """view in shell with a menu to run calibrolino"""

    _welcome_msg = 'welcome to the calibrolino menu'

    def __init__(self):
        self._menu = {
                '1': dict(
                    display='change credentials',
                    method=self._change_credentials,
                    ),
                'q': dict(
                    display='quit',
                    method=self._quit,
                    ),
                }
        self._running = True

    def start(self):
        print(self._welcome_msg)
        while self._running:
            self._print_menu()
            choice = input('please select:\n')
            try:
                self._menu[choice]['method']()
            except KeyError:
                print('please select a valid option')
            print('===')

    def _print_menu(self):
        for key, element in self._menu.items():
            print(key, element['display'])

    def _change_credentials(self):
        """
        change the credentials to connect and
        optionnally save them for next time

        """
        print('enter the new credentials')

    def _quit(self):
        """
        quit

        """
        print('goodbye')
        self._running = False
