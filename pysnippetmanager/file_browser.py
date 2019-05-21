# -*- coding: utf-8 -*-
__author__ = "Martin Schröder"
__copyright__ = "Copyright 2019, Martin Schröder"
__email__ = "m.schroeder@tu-berlin.de"

try:
    from tkinter import *
    from tkinter import messagebox
    from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
    from tkinter import ttk
except ImportError:
    raise ModuleNotFoundError
import os
from PIL import Image, ImageTk
from pysnippetmanager.utils import StringInputDialog
DIR_IMG = os.path.dirname(os.path.abspath(__file__)) + '/../img/folder.png'
FILE_IMG = os.path.dirname(os.path.abspath(__file__)) + '/../img/file.png'


class FileBrowser(ttk.Treeview):
    dir_img = None
    popup_active = False
    app = {}

    def __init__(self, *args, **kwargs):
        if "columns" not in kwargs:
            kwargs["columns"] = ('lexer',)

        if "show" not in kwargs:
            kwargs["show"] = "tree"

        if 'app' in kwargs:
            self.app = kwargs['app']
            del (kwargs['app'])

        super(FileBrowser, self).__init__(*args, **kwargs)
        self.heading('#0', text="Name")
        self.heading('lexer', text="Lexer")
        self.column('lexer', stretch=True, width=100)
        self.column('#0', stretch=True, width=300)
        self.bind("<<TreeviewSelect>>", self.select, "+")
        self.bind("<Button-3>", self.mouse_right, "+")
        # images
        self.dir_img = ImageTk.PhotoImage(Image.open(DIR_IMG))
        self.file_img = ImageTk.PhotoImage(Image.open(FILE_IMG))

    def add_item(self, iid, label, lexer_alias, parent=''):
        """
        add a new item to the snippet tree
        """
        self.add_group(parent)
        self.insert(parent, "end", iid, text=label, open=True, values=(lexer_alias,), image=self.file_img)

    def add_group(self, group_str):
        if group_str == '':
            return ''
        if group_str not in self.app.groups:
            glabel = group_str.split('/')[-1]
            gparent = group_str.replace('/' + glabel, '')
            gparent = '' if gparent == '/' else gparent
            self.add_group(gparent)
            self.app.groups[group_str] = [glabel, gparent]
            self.insert(self.app.groups[group_str][1], "end",
                        group_str,
                        text=glabel,
                        open=True, values=(), image=self.dir_img)
            # self.tree.image = self.dir_img
            return gparent
        else:
            return self.app.groups[group_str][1]

    def select(self, event=None):
        """
        todo move code to app
        :param event:
        :return:
        """
        self.app.save()
        iid = self.focus()
        if iid is None:
            return False
        if iid not in self.app.snippets:
            return False
        self.app.text.snippet = self.app.snippets[iid]
        self.app.lexer_option_menu.set(self.app.text.snippet.lexer_alias)

    def mouse_right(self, event=None):
        if self.popup_active:
            return

        iid = self.identify_row(event.y)
        rmenu = Menu(self.master, tearoff=0)

        def do_popup(event=None):
            # display the popup menu
            try:
                # rmenu.post(event.x_root+40, event.y_root+10, entry="0")
                rmenu.post(event.x_root, event.y_root)
            finally:
                # make sure to release the grab (Tk 8.0a1 only)
                rmenu.grab_release()

        def _new_folder(event=None):
            self.master.unbind("<ButtonRelease-1>")
            self.popup_active = False
            dir_dialog = StringInputDialog(self.master,
                                           "Name",
                                           window_title="Create new directory")
            dir_dialog.wait_for_input()
            if dir_dialog.get_string() is None:
                return 'break'
            subpath = dir_dialog.get_string()
            # create folder
            directory = os.path.join(self.app.base_dir, iid[1:], subpath)
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.add_group(os.path.join(iid, subpath))
            return 'break'

        def _new_file(event=None):
            self.master.unbind("<ButtonRelease-1>")
            self.popup_active = False
            self.app.new(iid)

        def _close_menu(event=None):
            self.master.unbind("<ButtonRelease-1>")
            self.popup_active = False
            rmenu.destroy()

        self.master.bind("<ButtonRelease-1>", _close_menu)
        if iid:
            # mouse pointer over an item
            self.focus(iid)
            if iid in self.app.snippets:
                # snipped selected
                pass
            else:
                # folder selected
                rmenu.add_command(label=' new file', command=_new_file)
                rmenu.add_separator()
                rmenu.add_command(label=' new folder', command=_new_folder)
        else:
            # no item selected
            iid = '/'
            rmenu.add_command(label=' new file', command=_new_file)
            rmenu.add_separator()
            rmenu.add_command(label=' new folder', command=_new_folder)
        self.popup_active = True
        do_popup()
