try:
    from tkinter import *
    from tkinter import messagebox
    from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
    from tkinter import ttk
except ImportError:
    raise ModuleNotFoundError
import os

DIR_IMG = os.path.dirname(os.path.abspath(__file__)) + '/../img/folder.png'
FILE_IMG = os.path.dirname(os.path.abspath(__file__)) + '/../img/file.png'


class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)

class StringInputDialog(object):
    """
    https://stackoverflow.com/questions/15522336/text-input-in-tkinter
    """
    e = None
    frame = None
    master = None
    root = None
    string = None

    def __init__(self, master, request_message, window_title=""):
        self.master = master
        self.root = Toplevel(master)
        self.root.title(window_title)
        self.frame = Frame(self.root)
        self.frame.pack()
        self.accept_input(request_message)

    def accept_input(self, request_message):
        r = self.frame

        k = Label(r, text=request_message)
        k.pack(side='left')
        self.e = Entry(r, text='Name')
        self.e.pack(side='left')
        self.e.focus_set()
        b = Button(r, text='CANCEL', command=self.cancel)
        b.pack(side='right')
        b = Button(r, text='OK', command=self.get_text)
        b.pack(side='right')

    def get_text(self):
        self.string = self.e.get()
        if self.string == '':
            self.string = None
        self.root.destroy()

    def cancel(self):
        self.string = None
        self.root.destroy()

    def get_string(self):
        return self.string

    def wait_for_input(self):
        self.master.wait_window(self.root)
