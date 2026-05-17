import tkinter
from tkinter import ttk, simpledialog


from pandastable import Table


from calibrolino.interfaces import View, Controller, ControllerException


class CredentialsPrompt(simpledialog.Dialog):
    """prompt to ask for new credentials"""

    def __init__(self, parent, partners: [str]):
        self._partners = partners
        super().__init__(parent)

    def body(self, master):
        """ """
        self._partners_list = ttk.Combobox(
            master,
            state='readonly',
            values=self._partners,
        )
        self._partners_list.set(self._partners[0])
        self._partners_list.grid(column=0, row=0, columnspan=2)
        ttk.Label(master, text='username:').grid(column=0, row=1)
        self._username = ttk.Entry(master)
        self._username.grid(column=1, row=1)
        ttk.Label(master, text='password:').grid(column=0, row=2)
        self._password = ttk.Entry(master)
        self._password.grid(column=1, row=2)
        self.new_credentials = None

    def apply(self):
        new_partner = self._partners_list.get()
        username = self._username.get()
        password = self._password.get()
        self.new_credentials = dict(
            partner=new_partner,
            username=username,
            password=password,
        )


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
        self._create_lib_table()
        self._options_frame = ttk.LabelFrame(self)
        self._options_frame.pack()
        self._create_buttons_in_options_frame()
        self.update()

    def _create_lib_table(self):
        synced_frame = ttk.LabelFrame(self._library_frame, text='synced books')
        synced_frame.pack(side=tkinter.LEFT)
        local_frame = ttk.LabelFrame(self._library_frame, text='local books')
        local_frame.pack(side=tkinter.LEFT)
        online_frame = ttk.LabelFrame(self._library_frame, text='online books')
        online_frame.pack(side=tkinter.LEFT)

        frame = synced_frame
        table_frame = ttk.Frame(frame)
        table_frame.pack()
        pt = Table(
            table_frame,
        )
        pt.show()
        self._synced_table = pt
        button_frame = ttk.Frame(frame)
        button_frame.pack()
        ttk.Button(
            button_frame,
            text='delete from online lib',
            command=self._delete_selected_book_online_from_sync,
        ).grid(column=0, row=0)
        ttk.Button(
            button_frame,
            text='delete from local lib',
            command=self._delete_selected_book_local_from_sync,
        ).grid(column=1, row=0)

        frame = local_frame
        table_frame = ttk.Frame(frame)
        table_frame.pack()
        pt = Table(
            table_frame,
        )
        pt.show()
        self._local_table = pt
        button_frame = ttk.Frame(frame)
        button_frame.pack()
        ttk.Button(
            button_frame,
            text='delete',
            command=self._delete_selected_book_local_from_local,
        ).grid(column=0, row=0)
        ttk.Button(
            button_frame,
            text='upload',
            command=self._upload_one,
        ).grid(column=1, row=0)

        frame = online_frame
        table_frame = ttk.Frame(frame)
        table_frame.pack()
        pt = Table(
            table_frame,
        )
        pt.show()
        self._online_table = pt
        button_frame = ttk.Frame(frame)
        button_frame.pack()
        ttk.Button(
            button_frame,
            text='delete',
            command=self._delete_selected_book_online_from_online,
        ).grid(column=0, row=0)
        ttk.Button(
            button_frame,
            text='download',
            command=self._download_one,
        ).grid(column=1, row=0)

    def _create_buttons_in_options_frame(self):
        """
        :returns: TODO

        """
        ttk.Button(
            self._options_frame,
            text='test',
            command=self._test,
        ).grid(column=0, row=0)
        ttk.Button(
            self._options_frame,
            text='refresh',
            command=self._update_library_display,
        ).grid(column=1, row=0)
        ttk.Button(
            self._options_frame,
            text='sync',
            command=self._sync,
        ).grid(column=2, row=0)
        ttk.Button(
            self._options_frame,
            text='check sync (slow)',
            command=self._check_sync,
        ).grid(column=3, row=0)
        ttk.Button(
            self._options_frame,
            text='upload all',
            command=self._upload_all,
        ).grid(column=0, row=1)
        ttk.Button(
            self._options_frame,
            text='download all',
            command=self._download_all,
        ).grid(column=0, row=2)

    def _autodetect_sync(self):
        self.controller.autodetect_to_sync_books()
        self._update_library_display()

    def _sync(self):
        try:
            self.controller.sync()
        except NotImplementedError:
            self.showerror('not implemented')
        self._update_library_display()

    def _check_sync(self):
        self.controller.check_sync()

    def _test(self):
        self.showinfo('test')

    def _prompt_credentials(
        self,
    ):
        """prompt to change credentials"""
        partners = self.controller.partners
        prompt = CredentialsPrompt(self, partners)
        new_credentials = prompt.new_credentials
        if new_credentials:
            self.controller.credentials = new_credentials
            self._update_library_display()

    def _del_credentials(self):
        """ """
        del self.controller.credentials
        self._update_library_display(False)

    def _create_menu(self):
        """put option in menu"""
        menubar = tkinter.Menu(self)
        self.config(menu=menubar)
        file_menu = tkinter.Menu(menubar)
        file_menu.add_command(
            label='set credentials...',
            command=self._prompt_credentials,
        )
        file_menu.add_command(
            label='delete credentials...',
            command=self._del_credentials,
        )
        file_menu.add_command(
            label='detect books to be synced...',
            command=self._autodetect_sync,
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
        if self.controller.credentials:
            self._update_library_display()
        else:
            self._update_library_display(include_online=False)
        self.mainloop()

    def _update_library_display(self, include_online=True):
        """ """
        df = self.controller.get_full_library(include_online)
        df_sync = df[(df['local_id'] != 0) & (df['online_id'] != '')]
        df_local = df[(df['local_id'] != 0) & (df['online_id'] == '')]
        df_online = df[(df['local_id'] == 0) & (df['online_id'] != '')]
        self._synced_table.model.df = df_sync
        self._synced_table.sortTable(1)
        self._synced_table.redraw()
        self._online_table.model.df = df_online
        self._online_table.sortTable(1)
        self._online_table.redraw()
        self._local_table.model.df = df_local
        self._local_table.sortTable(1)
        self._local_table.redraw()

    def _upload_all(self):
        """upload the whole library"""
        self.controller.sync_upload()
        self._update_library_display()

    def _download_all(self):
        self.controller.download_all()
        self._update_library_display()

    def _download_one(self):
        rowdata = self._online_table.getSelectedRowData()
        online_id = rowdata.index.values[0]
        try:
            self.controller.download_book(online_id)
        except ControllerException as e:
            self.showerror(e)
        else:
            self._update_library_display()

    def _upload_one(self):
        """upload selected book"""
        rowdata = self._local_table.getSelectedRowData()
        local_id = rowdata.index.values[0]
        self.controller.upload_book(local_id)
        self._update_library_display()

    def _delete_selected_book_online_from_sync(self):
        """delete selected book from the cloud"""
        rowdata = self._synced_table.getSelectedRowData()
        online_id = rowdata['online_id'].values[0]
        self.controller.delete_book(online_id)
        self._update_library_display()

    def _delete_selected_book_online_from_online(self):
        """delete selected book from the cloud"""
        rowdata = self._online_table.getSelectedRowData()
        online_id = rowdata.index.values[0]
        self.controller.delete_book(online_id)
        self._update_library_display()

    def _delete_selected_book_local_from_sync(self):
        """delete selected book from the local lib"""
        rowdata = self._sync_table.getSelectedRowData()
        book_id = rowdata['local_id'].values[0]
        self.controller.delete_book_locally(book_id)
        self._update_library_display()

    def _delete_selected_book_local_from_local(self):
        """delete selected book from the local lib"""
        rowdata = self._local_table.getSelectedRowData()
        book_id = rowdata.index.values[0]
        self.controller.delete_book_locally(book_id)
        self._update_library_display()

    def askokcancel(self, msg: str) -> bool:
        return tkinter.messagebox.askokcancel(message=msg)

    def askyesno(self, msg: str) -> bool:
        return tkinter.messagebox.askyesno(message=msg)


if __name__ == '__main__':
    view = CalibrolinoGUIView()
    answer = view.askyesno('are you sure?')
    print(answer)
    pass
