# -*- coding: utf-8 -*-
__author__ = "Martin Schröder"
__copyright__ = "Copyright 2019, Martin Schröder"
__email__ = "m.schroeder@tu-berlin.de"

from pygments.styles import get_style_by_name

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


class TextEditor(Text):
    """
    enhanced version of the Text input
    """
    content = ''
    lines = ''
    text = ''
    row = '0'
    _snippet = None
    _style = None
    font_size = 10
    font_name = 'monospace'
    style_name = 'colorful'

    def __init__(self, *args, **kwargs):
        if 'snippet' in kwargs:
            self.snippet = kwargs['snippet']
            del (kwargs['snippet'])
        super(TextEditor, self).__init__(*args, **kwargs)

        self.bind("<KeyRelease>", self.default_highlight)
        self.bind("<Control-Key-a>", self.select_all)
        self.bind("<1>", lambda event: self.focus_set())
        self.style = self.style_name

        self.tag_configure("Same", background="#ffff00")
        self.tag_configure(SEL, background="#ffff00")

    def configure_style(self):
        self.config(background=self._style.background_color,
                    font='%s %d' % (self.font_name, self.font_size))  # set background

        for token, format_dict in self._style.list_styles():
            self.tag_configure(str(token), **self.parse_pygments_style_format_dict(format_dict))

        self.tag_configure("Same", background="#ffff00")
        self.tag_configure(SEL, background="#ffff00")

    def parse_pygments_style_format_dict(self, format_dict):
        options = {}
        if format_dict['color'] is not None:
            options['foreground'] = '#' + format_dict['color']
        if format_dict['bgcolor'] is not None:
            options['background'] = '#' + format_dict['bgcolor']
        if format_dict['bold']:
            options['font'] = '%s %d bold' % (self.font_name, self.font_size)
        if format_dict['italic']:
            options['font'] = '%s %d italic' % (self.font_name, self.font_size)
        if format_dict['underline']:
            options['underline'] = True
        return options

    def parse_pygments_style_format_str(self, format_str):
        if format_str == '':
            return {}
        options = {}
        for item in format_str.split(' '):
            if 'border' in item:
                # format border is not supported
                continue
            elif 'bg:#' in item:
                options['background'] = '#' + item.split('#')[-1]
            elif 'bg:' in item:
                # transparent background
                continue
            elif '#' in item:
                options['foreground'] = '#' + item.split('#')[-1]
                continue
            elif 'bold' in item:
                options['font'] = '%s %d bold' % (self.font_name, self.font_size)
            elif 'italic' in item:
                options['font'] = '%s %d italic' % (self.font_name, self.font_size)
            elif 'nounderline' in item:
                options['underline'] = False
            elif 'underline' in item:
                options['underline'] = True
        return options

    def replace_text(self, *args, **kwargs):
        """
        replaces all the content in the text window
        """
        self.delete("1.0", END)
        self.insert(*args, **kwargs)

    def insert(self, *args, **kwargs):
        super(TextEditor, self).insert(*args, **kwargs)
        self.content = ''
        self.update_highlight()

    def default_highlight(self, event=None):
        if self.snippet is None:
            return None
        self.content = self.get("1.0", END)
        # self.lines = self.content.split("\n")
        if self.snippet.snippet != self.content:
            self.mark_set("range_start", self.row + ".0")
            # data = self.text.get(self.row + ".0", self.row + "." + str(len(self.lines[int(self.row) - 1])))
            for token, content in self.snippet.lexer.get_tokens(self.content):
                self.mark_set("range_end", "range_start + %dc" % len(content))
                self.tag_add(str(token), "range_start", "range_end")
                self.mark_set("range_start", "range_end")
        self.snippet.snippet = self.get("1.0", END)

    def update_highlight(self):
        if self.snippet is None:
            return None
        self.snippet.snippet = ''
        self.default_highlight()

    def remove_highlight(self):
        if self.snippet is None:
            return None
        self.content = self.get("1.0", END)
        # self.lines = self.content.split("\n")
        self.mark_set("range_start", self.row + ".0")
        # data = self.text.get(self.row + ".0", self.row + "." + str(len(self.lines[int(self.row) - 1])))
        for token, content in self.snippet.lexer.get_tokens(self.content):
            self.mark_set("range_end", "range_start + %dc" % len(content))
            self.tag_remove(str(token), "range_start", "range_end")
            self.mark_set("range_start", "range_end")

    def select_all(self, event=None):
        self.tag_add(SEL, "1.0", END)
        self.mark_set(INSERT, "1.0")
        self.see(INSERT)
        return 'break'

    @property
    def snippet(self):
        return self._snippet

    @snippet.setter
    def snippet(self, cs):
        self.remove_highlight()
        self._snippet = cs
        if cs is not None:
            self._snippet.bind("lexer_before_change", self.remove_highlight)
            self._snippet.bind("lexer_after_change", self.update_highlight)
            self.replace_text("1.0", self._snippet.snippet)

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style_name):
        if style_name == '':
            style_name = 'default'
        self._style = get_style_by_name(style_name)
        self.style_name = style_name
        self.configure_style()
