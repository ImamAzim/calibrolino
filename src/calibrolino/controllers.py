from varboxes import VarBox


from calibrolino.interfaces import Controller, View


class CalibrolinoController(Controller):

    """controller of calibrolino in mvc arch"""

    def __init__(self, view: View):
        Controller.__init__(self)
        self._view = view
        self._varbox = VarBox('calibrolino')

    @property
    def credentials(self) -> dict:
        try:
            credentials = dict(
                    partner=self._varbox.partner,
                    username=self._varbox.username,
                    password=self._varbox.password,
                    )
        except AttributeError:
            credentials = None
        return credentials

    @credentials.setter
    def credentials(self, value: dict):
        self._varbox.partner = value['partner']
        self._varbox.username = value['username']
        self._varbox.password = value['password']
