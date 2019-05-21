# -*- coding: utf-8 -*-
__author__ = "Martin Schröder"
__copyright__ = "Copyright 2019, Martin Schröder"
__email__ = "m.schroeder@tu-berlin.de"

from pygments.lexers import get_lexer_by_name
from pygments.lexer import Lexer
from pygments.util import ClassNotFound

try:
    from tkinter import *
    from tkinter import messagebox
    from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
    from tkinter import ttk
except ImportError:
    raise ModuleNotFoundError
import os
from shutil import copy2

from datetime import datetime

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
    parse_header_done = False
    parse_snippet_done = False
    snippet_changed = False

    def __init__(self, filename, lexer_alias=None, create=False, base_dir='~/'):
        """
        constructor of the  snippet object
        """
        self.filename = os.path.expanduser(filename)
        self.label = os.path.splitext(os.path.split(self.filename)[-1])[0]
        self.group = os.path.split(self.filename)[0].replace(os.path.expanduser(base_dir), '')
        self.events = dict(lexer_after_change=[], lexer_before_change=[])
        if create and lexer_alias is not None:
            self.lexer_alias = lexer_alias
            self.lexer = get_lexer_by_name(self.lexer_alias)
            self.tags = []
            self.save()
        else:
            self.parse_file(header_only=True)

    def parse_file(self, header_only=False):
        """
        parse the file
        """
        with open(self.filename, 'r') as f:
            _header = f.readline()  # extract header
            self.header = _header
            if not header_only:
                self.snippet = f.read()

    def save(self):
        """
        save snippet to file
        """
        if not self.snippet_changed:
            return False
        backup_dir = os.path.expanduser(os.path.join(os.path.dirname(self.filename), '.backup'))
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        copy2(self.filename, os.path.join(backup_dir,
                                          self.label + '%s' % datetime.strftime(datetime.now(),
                                                                                '_%Y%m%d_%H%M%S') + '.pycsm'))
        with open(self.filename, 'w') as f:
            f.write(self.header + '\n')
            f.write(self.snippet)
        self.snippet_changed = False

    @property
    def header(self):
        """
        get header
        """
        if not self.parse_header_done:
            self.parse_file()
        _header = self.lexer_alias
        for tag in self.tags:
            _header += ', %s' % tag
        return _header

    @header.setter
    def header(self, value):
        """ parse header
        structure: lexer, tag, tag, tag
        """
        _header = value.split(',')
        self.tags = []
        if len(_header) == 0:
            self.lexer = None
        else:
            self.lexer = _header.pop(0).strip()
            self.tags = []
            for tag in _header:
                self.tags.append(tag.strip())
        self.parse_header_done = True

    @property
    def snippet(self):
        if not self.parse_snippet_done:
            self.parse_file()
        return self._raw_snippet

    @snippet.setter
    def snippet(self, new_snippet):
        if self.parse_snippet_done:
            self.snippet_changed = True
        self._raw_snippet = new_snippet
        self.parse_snippet_done = True

    @property
    def lexer(self):
        return self._lexer

    @lexer.setter
    def lexer(self, value):
        self.trigger_event("lexer_before_change")
        if value is None:
            self._lexer = get_lexer_by_name("text")
        elif type(value) is str:
            try:
                self._lexer = get_lexer_by_name(value)
            except ClassNotFound:
                self._lexer = get_lexer_by_name('text')
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

    def trigger_event(self, event):
        if event in self.events:
            for e in self.events[event]:
                e()

    def bind(self, event, function_handle):
        if event in self.events:
            self.events[event].append(function_handle)
