import getpass
import tkinter
from tkinter import ttk


from pandastable import Table


from calibrolino.interfaces import View, Controller


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
        self.update()

    def _create_menu(self):
        """put option in menu

        """
        menubar = tkinter.Menu(self)
        self.config(menu=menubar)
        file_menu = tkinter.Menu(menubar)
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
        pt.show()
        print(full_lib)

    def _change_credentials(self):
        """
        change the credentials to connect and
        save them for next time

        """
        pass

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
