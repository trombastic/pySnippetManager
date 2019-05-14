# -*- coding: utf-8 -*-
""" A Snippet Manager written in Python


"""
__author__ = "Martin Schröder"
__copyright__ = "Copyright 2019, Martin Schröder"
__credits__ = []
__license__ = "GPLv3"
__version__ = "0.1.1"
__maintainer__ = "Martin Schröder"
__email__ = "m.schroeder@tu-berlin.de"
__status__ = "Alpha"
__docformat__ = 'reStructuredText'

from pygments import highlight, lex
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.lexer import Lexer
from pygments.formatters import HtmlFormatter
try:
    from tkinter import *
    from tkinter import messagebox
    from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
    from tkinter import ttk
except:
    from Tkinter import *
import os
import sys
import re
import fnmatch
from PIL import Image, ImageTk

DIR_IMG = os.path.dirname(os.path.abspath(__file__)) + '/../img/folder.png'
FILE_IMG = os.path.dirname(os.path.abspath(__file__)) + '/../img/file.png'

class Snippet(object):
    """ A Snippet Object
    
    """
    _lexer = None  # the programming language of the  Snippet
    lexer_alias = ''  # 
    group = 'base'  # list of all groups
    tags = []
    label = 'none'  # the label of the  Snippet
    attachments = []  # a list of attachments
    _raw_snippet = ''  # 
    filename = None  # name and location of the file holding the  snippet
    events = {}
    def __init__(self, filename, lexer_alias=None, create=False, base_dir='~/'):
        """
        constructor of the  snippet object
        """
        self.filename = os.path.expanduser(filename)
        self.label = os.path.splitext(os.path.split(self.filename)[-1])[0]
        self.group = os.path.split(self.filename)[0].replace(os.path.expanduser(base_dir),'')
        self.events = dict(lexer_after_change=[],lexer_befor_change=[])
        if create and lexer_alias is not None:
            self.lexer_alias = lexer_alias
            self.lexer = get_lexer_by_name(self.lexer_alias)
            self.tags = []
            self.save()
        else:
            self.parse_file()
    
    def parse_file(self):
        """
        parse the file
        """
        with open(self.filename,'r') as f:
            self.header = f.readline()
            self.snippet = f.read()
    
    def save(self):
        """
        save to file
        """
        
        with open(self.filename,'w') as f:
            f.write(self.header + '\n')
            f.write(self.snippet)
    
    @property
    def header(self):
        """
        
        """
        _header = self.lexer_alias
        for tag in self.tags:
            _header += ', %s'%tag
        return _header
    
    @header.setter
    def header(self, value):
        """
        structure: lexer, tag, tag, tag
        """
        _header = value.split(',')
        self.tags = []
        if len(_header) == 0:
            self.lexer = None
            return None
        self.lexer = _header.pop(0).strip()
        self.tags = []
        for tag in _header:
            self.tags.append(tag.strip())
    
    @property
    def snippet(self):
        return self._raw_snippet
    
    @snippet.setter
    def snippet(self,new_snippet):
        self._raw_snippet = new_snippet

    @property
    def lexer(self):
        return self._lexer
    
    @lexer.setter
    def lexer(self, value):
        self.trigger_event("lexer_befor_change")
        if value is None:
            self._lexer = get_lexer_by_name("text")
        elif type(value) is str:
            try:
                self._lexer = get_lexer_by_name(value)
            except:
                self._lexer = get_lexer_by_name('text')  # todo change to text
            self.lexer_alias = self._lexer.aliases[0]
        elif isinstance(value, Lexer):
            self._lexer = value
            self.lexer_alias = value.aliases[0]
        elif issubclass(value, Lexer):
            self._lexer = value()
            self.lexer_alias = value.aliases[0]
        else:
            self._lexer = None
            self.lexer_alias = None
        self.trigger_event("lexer_after_change")
        
    def trigger_event(self,event):
        if event in self.events:
            for e in self.events[event]:
                e()
                print(e)
    
    def bind(self,event,function_handle):
        if event in self.events:
            self.events[event].append(function_handle)
        
class TextEditor(Text):
    """
    enhanced version of the Text input
    """
    content = ''
    lines = ''
    text = ''
    row = '0'
    _snippet = None
    def __init__(self,*args,**kwargs):
        if 'snippet' in kwargs:
            self.snippet = kwargs['snippet']
            del(kwargs['snippet'])
        super(TextEditor, self).__init__(*args,**kwargs)
        
        self.bind("<KeyRelease>", self.default_highlight)
        self.bind("<Control-Key-a>", self.select_all)
        self.bind("<1>", lambda event: self.focus_set())
        self.tag_configure("Token.Keyword", foreground="#CC7A00")
        self.tag_configure("Token.Keyword.Constant", foreground="#CC7A00")
        self.tag_configure("Token.Keyword.Declaration", foreground="#CC7A00")
        self.tag_configure("Token.Keyword.Namespace", foreground="#CC7A00")
        self.tag_configure("Token.Keyword.Pseudo", foreground="#CC7A00")
        self.tag_configure("Token.Keyword.Reserved", foreground="#CC7A00")
        self.tag_configure("Token.Keyword.Type", foreground="#CC7A00")
        
        self.tag_configure("Token.Operator.Word",foreground="#CC7A00")
        
        self.tag_configure("Token.Name.Class", foreground="#003D99")
        self.tag_configure("Token.Name.Exception", foreground="#003D99")
        self.tag_configure("Token.Name.Function", foreground="#003D99")
        self.tag_configure("Token.Name.Namespace", foreground="#003D99")
        self.tag_configure("Token.Name.Builtin",foreground="#CC7A00")
        self.tag_configure("Token.Name.Builtin.Pseudo", foreground="#003D99")

        self.tag_configure("Token.Comment", foreground="#B80000")
        self.tag_configure("Token.Comment.Single", foreground="#B80000")
        self.tag_configure("Token.Comment.Hashbang", foreground="#B80000")

        self.tag_configure("Token.Literal.String", foreground="#248F24")
        self.tag_configure("Token.Literal.String.Double", foreground="#248F24")
        self.tag_configure("Token.Literal.String.Single", foreground="#248F24")
        self.tag_configure("Token.Literal.String.Doc", foreground="#248F24")

        #self.tag_configure("Token.Text", foreground="#248F24", background="#eeeeee")
        self.tag_configure("Token.Text.Whitespace.Leading0", foreground="#248F24", background="#ccffcc")
        self.tag_configure("Token.Text.Whitespace.Leading1", foreground="#248F24", background="#ccffff")
        self.tag_configure("Token.Text.Whitespace.Leading2", foreground="#248F24", background="#ccccff")
        self.tag_configure("Token.Text.Whitespace.Newline", foreground="#248F24", background="#dddddd")
        #self.tag_configure("Token.Text.Whitespace.Trailing", foreground="#248F24", background="#eeeeee")

        self.tag_configure("Bracket.Token.Punctuation.Bracket1", foreground="#ffffff", background="#000000")
        self.tag_configure("Bracket.Token.Punctuation.Bracket2", foreground="#ffffff", background="#555555")
        self.tag_configure("Bracket.Token.Punctuation.Bracket3", foreground="#000000", background="#999999")
        self.tag_configure("Bracket.Token.Punctuation.Bracket4", foreground="#000000", background="#cccccc")
        self.tag_configure("Bracket.Token.Punctuation.Bracket5", foreground="#ffffff", background="#000000")
        self.tag_configure("Bracket.Token.Punctuation.Bracket6", foreground="#ffffff", background="#555555")
        self.tag_configure("Bracket.Token.Punctuation.Bracket7", foreground="#000000", background="#999999")
        self.tag_configure("Bracket.Token.Punctuation.Bracket8", foreground="#000000", background="#cccccc")

        self.tag_configure("Same", background="#ffff00")
        self.tag_configure(SEL, background="#ffff00")
        
    
    def replace_text(self,*args,**kwargs):
        """
        replaces all the content in the text window
        """
        self.delete("1.0",END)
        self.insert(*args,**kwargs)
    
    def insert(self,*args,**kwargs):
        super(TextEditor, self).insert(*args,**kwargs)
        self.content = ''
        self.update_highlight()
    
    def default_highlight(self, *args,**kwargs):
        if self.snippet is None:
            return None
        self.content = self.get("1.0", END)
        #self.lines = self.content.split("\n")
        if (self.snippet.snippet != self.content):
            self.mark_set("range_start", self.row + ".0")
            #data = self.text.get(self.row + ".0", self.row + "." + str(len(self.lines[int(self.row) - 1])))
            for token, content in self.snippet.lexer.get_tokens(self.content):
                self.mark_set("range_end", "range_start + %dc" % len(content))
                self.tag_add(str(token), "range_start", "range_end")
                self.mark_set("range_start", "range_end")
        self.snippet.snippet = self.get("1.0", END)
    
    def update_highlight(self):
        self.previousContent = ''
        self.default_highlight()
    
    def remove_highlight(self):
        if self.snippet is None:
            return None
        self.content = self.get("1.0", END)
        #self.lines = self.content.split("\n")
        self.mark_set("range_start", self.row + ".0")
        #data = self.text.get(self.row + ".0", self.row + "." + str(len(self.lines[int(self.row) - 1])))
        for token, content in self.snippet.lexer.get_tokens(self.content):
            self.mark_set("range_end", "range_start + %dc" % len(content))
            self.tag_remove(str(token), "range_start", "range_end")
            self.mark_set("range_start", "range_end")
    
    def select_all(self,event=None):
        self.tag_add(SEL, "1.0", END)
        self.mark_set(INSERT, "1.0")
        self.see(INSERT)
        return 'break'
    
    @property
    def snippet(self):
        return self._snippet
    
    @snippet.setter
    def snippet(self,cs):
        self.remove_highlight()
        self._snippet = cs
        if cs is not None:
            self._snippet.bind("lexer_befor_change",self.remove_highlight)
            self._snippet.bind("lexer_after_change",self.update_highlight)
            self.replace_text("1.0", self._snippet.snippet)

class StringInputDialog(object):
    """
    https://stackoverflow.com/questions/15522336/text-input-in-tkinter
    """
    def __init__(self,master,request_message):
        self.master = master
        self.root = Toplevel(master)
        self.string = None
        self.frame = Frame(self.root)
        self.frame.pack()
        self.accept_input(request_message)

    def accept_input(self,request_message):
        r = self.frame

        k = Label(r,text=request_message)
        k.pack(side='left')
        self.e = Entry(r,text='Name')
        self.e.pack(side='left')
        self.e.focus_set()
        b = Button(r,text='OK',command=self.get_text)
        b.pack(side='right')
        b = Button(r,text='CANCLE',command=self.cancle)
        b.pack(side='right')

    def get_text(self):
        self.string = self.e.get()
        print(self.string)
        self.root.destroy()
    
    def cancle(self):
        self.string = None
        self.root.destroy()
    
    def get_string(self):
        return self.string

    def wait_for_input(self):
        self.master.wait_window(self.root)

class App(object):
    """
    the gui
    """
    frame = None
    snippets = None
    groups =  None
    last_dir = "~/"
    base_dir = "~/"
    lexer_options = None
    lexers = None
    lexer_option_menu = None
    id = 0
    dir_img = None
    popup_active = False
    def __init__(self, master):
        self.init_lexers()
        self.master = master
        self.frame = Frame(master)
        #self.frame.grid()
        self.text = TextEditor(self.frame)
        self.treeview = ttk.Treeview(self.frame,show="tree",columns=('lexer',))
        self.treeview.heading('#1', text="Lexer")

        self.treeview.pack(side=LEFT,fill="both",expand=True)
        self.treeview.bind("<<TreeviewSelect>>", self.tree_select, "+")
        self.treeview.bind("<Button-3>", self.tree_mouse_right, "+")
        # create a toolbar
        toolbar = Frame(master)
        self.lexer_options = StringVar(toolbar)
        self.lexer_option_menu = ttk.Combobox(toolbar, textvariable=self.lexer_options, values=list(self.lexers.keys()))
        self.lexer_option_menu.bind("<<ComboboxSelected>>", self.lexer_selected)
        self.lexer_option_menu.bind("<FocusOut>", self.lexer_selected)
        b = Button(toolbar, text="NEW", width=6, command=self.new)
        b.pack(side=LEFT, padx=2, pady=2)
        #b = Button(toolbar, text="OPEN", width=6, command=self.open)
        #b.pack(side=LEFT, padx=2, pady=2)
        b = Button(toolbar, text="SAVE", width=6, command=self.save)
        b.pack(side=LEFT, padx=2, pady=2)
        #b = Button(toolbar, text="CLOSE", width=6, command=self.close)
        #b.pack(side=LEFT, padx=2, pady=2)
        b = Button(toolbar, text="QUIT", width=6, command=self.quit)
        b.pack(side=LEFT, padx=2, pady=2)
        self.lexer_option_menu.pack(side=LEFT, padx=2, pady=2)
        toolbar.pack(side=TOP, fill=X)
        
        
        # create the text window
        self.text.pack(side=BOTTOM,fill=X)
        self.text.insert("1.0","")
        self.frame.pack()
        
        # images
        self.dir_img = ImageTk.PhotoImage(Image.open(DIR_IMG))
        self.file_img = ImageTk.PhotoImage(Image.open(FILE_IMG))
        
        # init content
        self.read_config()
        self.crawler()
        
        
    
    def init_lexers(self):
        """
        get all availible lexers 
        """
        self.lexers = {}
        for lexer in get_all_lexers():
            self.lexers[lexer[1][0]] = lexer
    
    def read_config(self):
        """
        read the configuration file
        """
        if os.path.exists(os.path.expanduser('~/.pySnippetManager')):
            with open(os.path.expanduser('~/.pySnippetManager'),'r') as f:
                self.base_dir = f.readline()
        else:
            if self.open_base_dir():
                with open(os.path.expanduser('~/.pySnippetManager'),'w') as f:
                    f.write(self.base_dir)

    
    def crawler(self):
        """
        crawl all files in a directory
        """
        self.snippets = {}
        self.groups = {}
        self.id = 0
        includes = ['*.pycsm'] # for files only
        includes = r'|'.join([fnmatch.translate(x) for x in includes])
        for root, subdirs, files in os.walk(self.base_dir):
            files = [f for f in files if re.match(includes, f)]
            for file in files:
                self.snippets['%d'%self.id] = Snippet(filename=os.path.join(root,file),
                                                               base_dir=self.base_dir)
                self.tree_add_item(iid=self.id,
                                   label=self.snippets['%d'%self.id].label,
                                   lexer_alias=self.snippets['%d'%self.id].lexer_alias,
                                   parent=self.snippets['%d'%self.id].group)
                self.id += 1
            for subdir in subdirs:
                #print()
                self.tree_add_group(os.path.join(root,subdir).replace(os.path.expanduser(self.base_dir),''))

    def tree_add_item(self, iid, label, lexer_alias, parent=''):
        """
        
        """
        self.tree_add_group(parent)
        self.treeview.insert(parent, "end", iid, text=label, open=True, values=(lexer_alias,),image=self.file_img)
    
    def tree_add_group(self,group_str):
        if group_str == '':
            return ''
        if group_str not in self.groups:
            glabel = group_str.split('/')[-1]
            gparent = group_str.replace('/'+glabel,'')
            gparent = '' if gparent == '/' else gparent
            self.tree_add_group(gparent)
            self.groups[group_str] = [glabel, gparent]
            self.treeview.insert(self.groups[group_str][1], "end",
                                    group_str, 
                                    text=glabel, 
                                    open=True, values=(),image=self.dir_img)
            #self.treeview.image = self.dir_img
            return gparent
        else:
            self.groups[group_str][1]
    
    def tree_select(self, event=None):
        self.save()
        iid = self.treeview.focus()
        if iid is None:
            return False
        if iid not in self.snippets:
            return False
        self.text.snippet = self.snippets[iid]
        self.lexer_option_menu.set(self.text.snippet.lexer_alias)
    
    def tree_mouse_right(self, event=None):
        #print(self.treeview.focus())
        # select row under mouse
        if self.popup_active:
            return
        
        iid = self.treeview.identify_row(event.y)
        rmenu = Menu(self.master, tearoff=0)
        
        def do_popup(event):
            # display the popup menu
            try:
                #rmenu.post(event.x_root+40, event.y_root+10, entry="0")
                rmenu.post(event.x_root, event.y_root)
            finally:
                # make sure to release the grab (Tk 8.0a1 only)
                rmenu.grab_release()
        
        def _new_folder(event=None):
            self.master.unbind("<ButtonRelease-1>")
            self.popup_active = False
            print(iid)
            dir_dialog = StringInputDialog(self.master, 'Dir Nname')
            dir_dialog.wait_for_input()
            print(dir_dialog.get_string())
            if dir_dialog.get_string() is None:
                return 'break'
            subpath = dir_dialog.get_string()
            # create folder
            directory = os.path.join(self.base_dir, iid[1:], subpath)
            print(directory)
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.tree_add_group(os.path.join(iid,subpath))
            return 'break'
        
        def _new_file(event=None):
            self.master.unbind("<ButtonRelease-1>")
            self.popup_active = False
            self.new(iid)
            
        
        def _close_menu(event=None):
            self.master.unbind("<ButtonRelease-1>")
            self.popup_active = False
            rmenu.destroy()
        
        self.master.bind("<ButtonRelease-1>",_close_menu)
        if iid:
            # mouse pointer over an item
            self.treeview.focus(iid)
            if iid in self.snippets:
                # snipped selected
                pass
            else:
                # folder selected
                rmenu.add_command(label=' new file', command=_new_file)
                rmenu.add_separator()
                rmenu.add_command(label=' new folder', command=_new_folder)
                
            #print(event.x_root, event.y_root)            
        else:
            # no item selected
            rmenu.add_command(label=' new file', command=_new_file)
            rmenu.add_separator()
            rmenu.add_command(label=' new folder', command=_new_folder)
        self.popup_active = True
        do_popup(event)

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
                                   filetypes = (("Snippet Files","*.pycsm"),
                                                ("all files","*.*")))
        if filename is None:
            return False
        if len(filename) == 0:
            return False
        self.last_dir = os.path.dirname(os.path.abspath(filename)) 
        self.text.snippet = Snippet(filename=filename,base_dir=self.base_dir)
        self.lexer_option_menu.set(self.snippet.lexer_alias)
    
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
        
        filename = asksaveasfilename(initialdir=os.path.join(self.base_dir,subpath[1:]), 
                                     title="Select file", 
                                     filetypes=(("Snippet Files","*.pycsm"),
                                                ("all files","*.*")))
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
        # todo add to treeview
        self.snippets['%d'%self.id] = self.text.snippet
        self.tree_add_item(iid=self.id,
                        label=self.snippets['%d'%self.id].label,
                        lexer_alias=self.snippets['%d'%self.id].lexer_alias,
                        parent=self.snippets['%d'%self.id].group)
        self.id += 1
    
    def lexer_selected(self, event=None):
        """
        
        """
        if self.text.snippet is not None:
            self.text.snippet.lexer = self.lexer_option_menu.get()
            self.lexer_option_menu.set(self.text.snippet.lexer_alias)

def run():
    root = Tk() #Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    """
    the main code block
    """
    run()
