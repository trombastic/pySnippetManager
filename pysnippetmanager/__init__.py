# -*- coding: utf-8 -*-
""" A Snippet Manager written in Python


"""
__author__ = "Martin Schröder"
__copyright__ = "Copyright 2019, Martin Schröder"
__credits__ = []
__license__ = "GPLv3"
__version__ = "0.1.4"
__maintainer__ = "Martin Schröder"
__email__ = "m.schroeder@tu-berlin.de"
__status__ = "Alpha"
__docformat__ = 'reStructuredText'

try:
    from tkinter import *
except ImportError:
    raise ModuleNotFoundError

from pysnippetmanager.app import App


def run():
    root = Tk()  # Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    """
    the main code block
    """
    run()
