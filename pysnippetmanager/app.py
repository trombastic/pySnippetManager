from pygments.lexers import get_all_lexers
from pygments.styles import STYLE_MAP

try:
    from tkinter import *
    from tkinter import messagebox
    from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
    from tkinter import ttk
except ImportError:
    raise ModuleNotFoundError
import os
import re
import fnmatch
from pysnippetmanager.file_browser import FileBrowser
from pysnippetmanager.text_editor import TextEditor
from pysnippetmanager.snippet import Snippet


class App(object):
    """
    the gui
    """
    frame = None
    snippets = {}
    groups = {}
    last_dir = "~/"
    base_dir = "~/"
    lexer_options = None
    lexers = None
    lexer_option_menu = None
    id = 0

    def __init__(self, master):
        self.init_lexers()
        self.master = master
        self.frame = Frame(master)
        self.frame2 = Frame(master, width=400)
        self.master.winfo_toplevel().title("pySnippetManager")

        self.text = TextEditor(self.frame)
        self.tree = FileBrowser(self.frame2, app=self)

        # create a toolbar
        toolbar = Frame(master)

        # select lexer menu
        self.lexer_options = StringVar(toolbar)
        self.lexer_option_menu = ttk.Combobox(toolbar, textvariable=self.lexer_options, values=list(self.lexers.keys()))
        self.lexer_option_menu.bind("<<ComboboxSelected>>", self.lexer_selected)
        self.lexer_option_menu.bind("<FocusOut>", self.lexer_selected)
        # select highlight style menu
        self.style_options = StringVar(toolbar)
        self.style_option_menu = ttk.Combobox(toolbar, textvariable=self.style_options, values=list(STYLE_MAP.keys()))
        self.style_option_menu.bind("<<ComboboxSelected>>", self.style_selected)
        self.style_option_menu.bind("<FocusOut>", self.style_selected)
        self.style_option_menu.set(self.text.style_name)

        b_new = Button(toolbar, text="NEW", width=6, command=self.new)
        b_save = Button(toolbar, text="SAVE", width=6, command=self.save)
        b_rd = Button(toolbar, text="RESCAN DIR", width=10, command=self.crawler)
        b_quit = Button(toolbar, text="QUIT", width=6, command=self.quit)
        l_lang = Label(toolbar, text="Lang")
        l_style = Label(toolbar, text="Style")

        b_new.pack(side=LEFT, padx=2, pady=2)
        b_save.pack(side=LEFT, padx=2, pady=2)
        b_rd.pack(side=LEFT, padx=2, pady=2)
        b_quit.pack(side=LEFT, padx=2, pady=2)
        l_lang.pack(side=LEFT, padx=2, pady=2)
        self.lexer_option_menu.pack(side=LEFT, padx=2, pady=2)
        l_style.pack(side=LEFT, padx=2, pady=2)
        self.style_option_menu.pack(side=LEFT, padx=2, pady=2)
        toolbar.pack(side=TOP, fill=X)

        self.tree.pack(side=LEFT, fill=Y, expand=YES)

        self.text.pack(side=LEFT, fill=BOTH, expand=YES)
        self.text.insert("1.0", "")

        self.frame2.pack(side=LEFT, fill=Y, expand=NO)
        self.frame.pack(side=LEFT, fill=BOTH, expand=YES)

        # init content
        self.read_config()
        self.crawler()

    def init_lexers(self):
        """
        get all available lexers
        """
        self.lexers = {}
        for lexer in get_all_lexers():
            self.lexers[lexer[1][0]] = lexer

    def read_config(self):
        """
        read the configuration file
        """
        if os.path.exists(os.path.expanduser('~/.pySnippetManager')):
            with open(os.path.expanduser('~/.pySnippetManager'), 'r') as f:
                self.base_dir = f.readline()
        else:
            if self.open_base_dir():
                with open(os.path.expanduser('~/.pySnippetManager'), 'w') as f:
                    f.write(self.base_dir)

    def crawler(self):
        """
        crawl all files in the base directory
        """
        for iid in self.snippets.keys():
            self.tree.delete(iid)
        for iid in self.groups.keys():
            self.tree.delete(iid)

        self.snippets = {}
        self.groups = {}
        self.id = 0

        includes = ['*.pycsm']  # for files only
        includes = r'|'.join([fnmatch.translate(x) for x in includes])
        for root, subdirs, files in os.walk(self.base_dir):

            files = [f for f in files if re.match(includes, f)]
            for file in files:
                if '.backup' in root:
                    continue
                self.snippets['%d' % self.id] = Snippet(filename=os.path.join(root, file),
                                                        base_dir=self.base_dir)
                self.tree.add_item(iid=self.id,
                                   label=self.snippets['%d' % self.id].label,
                                   lexer_alias=self.snippets['%d' % self.id].lexer_alias,
                                   parent=self.snippets['%d' % self.id].group)
                self.id += 1
            for subdir in subdirs:
                if subdir == '.backup':
                    continue
                self.tree.add_group(os.path.join(root, subdir).replace(os.path.expanduser(self.base_dir), ''))

    def save(self):
        """
        save the current Snippet
        """
        if self.text.snippet is not None:
            self.text.snippet.save()

    def quit(self):
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            self.save()
            self.master.destroy()

    def close(self):
        """
        close the current Snippet
        """
        self.text.snippet = None

    def open(self):
        """
        open a new Snippet
        """
        filename = askopenfilename(initialdir=self.last_dir,
                                   filetypes=(("Snippet Files", "*.pycsm"),
                                              ("all files", "*.*")))
        if filename is None:
            return False
        if len(filename) == 0:
            return False
        self.last_dir = os.path.dirname(os.path.abspath(filename))
        self.text.snippet = Snippet(filename=filename, base_dir=self.base_dir)
        self.lexer_option_menu.set(self.text.snippet.lexer_alias)

    def open_base_dir(self):
        """
        open the base dir
        """
        filename = askdirectory(initialdir=self.base_dir,
                                title="Select Dir")
        if filename is None:
            return False
        if len(filename) == 0:
            return False
        self.base_dir = filename
        return True

    def new(self, subpath=''):
        """
        create a new Snippet
        """

        filename = asksaveasfilename(initialdir=os.path.join(self.base_dir, subpath[1:]),
                                     title="Select file",
                                     filetypes=(("Snippet Files", "*.pycsm"),
                                                ("all files", "*.*")))
        if filename is None:
            return False
        if len(filename) == 0:
            return False
        self.text.snippet = Snippet(filename=filename,
                                    lexer_alias='text',
                                    create=True,
                                    base_dir=self.base_dir)
        self.lexer_option_menu.set(self.text.snippet.lexer_alias)
        self.last_dir = os.path.dirname(os.path.abspath(filename))
        self.snippets['%d' % self.id] = self.text.snippet
        self.tree.add_item(iid=self.id,
                           label=self.snippets['%d' % self.id].label,
                           lexer_alias=self.snippets['%d' % self.id].lexer_alias,
                           parent=self.snippets['%d' % self.id].group)
        self.id += 1

    def lexer_selected(self, event=None):
        """

        """
        if self.text.snippet is not None:
            self.text.snippet.lexer = self.lexer_option_menu.get()
            self.lexer_option_menu.set(self.text.snippet.lexer_alias)

    def style_selected(self, event=None):
        """

        """
        if self.text.snippet is not None:
            self.text.style = self.style_option_menu.get()
