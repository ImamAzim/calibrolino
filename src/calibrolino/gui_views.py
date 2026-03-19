import getpass
import tkinter
from tkinter import ttk, simpledialog


from pandastable import Table


from calibrolino.interfaces import View, Controller


class CredentialsPrompt(simpledialog.Dialog):

    """prompt to ask for new credentials """

    def __init__(self, parent, partners: [str]):
        self._partners = partners
        super().__init__(parent)

    def body(self, master):
        """
        """
        pass
        # self._save_games_list = ttk.Combobox(
                # master,
                # state='readonly',
                # values=self._saved_games,
                # )
        # self._save_games_list.set(self._saved_games[0])
        # self._save_games_list.pack()
        # self.game_name = False
        self.new_credentials = None

    def apply(self):
        pass
        # self.game_name = self._save_games_list.get()


class CalibrolinoGUIView(View, tkinter.Tk):

    """GUI view run calibrolino"""

    _welcome_msg = 'welcome to the calibrolino menu'

    @property
    def controller(self) -> Controller:
        return self._controller

    @controller.setter
    def controller(self, value: Controller):
        self._controller = value

    def showerror(self, msg: str):
        tkinter.messagebox.showerror(
                title='error',
                message=msg,
                )

    def showinfo(self, msg: str):
        tkinter.messagebox.showinfo(
                title='info',
                message=msg,
                )

    def __init__(self):
        tkinter.Tk.__init__(self)
        self._create_menu()
        self._library_frame = ttk.LabelFrame(self)
        self._library_frame.pack()
        self._options_frame = ttk.LabelFrame(self)
        self._options_frame.pack()
        ttk.Button(self._options_frame, text='show selec', command=self._test).pack()
        self.update()

    def _test(self):
        rowdata = self._library_table.getSelectedRowData()
        index = rowdata.index
        title = index.values[0]
        print(title)

    def _prompt_credentials(self, ):
        """prompt to change credentials


        """
        partners = self.controller.partners
        prompt = CredentialsPrompt(partners)
        new_credentials = prompt.new_credentials
        if new_credentials:
            self.controller.credentials = new_credentials

    def _create_menu(self):
        """put option in menu

        """
        menubar = tkinter.Menu(self)
        self.config(menu=menubar)
        file_menu = tkinter.Menu(menubar)
        file_menu.add_command(
                label='set credentials...',
                command=self._prompt_credentials,
                )
        file_menu.add_command(
                label='quit',
                command=self.destroy,
                )
        menubar.add_cascade(
                label='File',
                menu=file_menu,
                underline=0,
                )

    def start(self):
        self._update_library_display()
        self.mainloop()

    def _update_library_display(self):
        """

        """
        full_lib = self.controller.get_full_library()
        pt = Table(
                self._library_frame,
                dataframe=full_lib,
                )
        pt.showindex = True
        pt.show()
        self._library_table = pt

    def _change_credentials(self):
        """
        change the credentials to connect and
        save them for next time

        """
        self.showinfo('TODO: prompt cred')

    def _upload_all(self):
        """upload the whole library

        """
        self.controller.sync_upload()

    def _upload_one(self):
        """upload only one book (for a test)

        """
        pass


if __name__ == '__main__':
    pass
