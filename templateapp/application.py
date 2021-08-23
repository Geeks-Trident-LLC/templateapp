"""Module containing the logic for the Template application."""

import tkinter as tk
# from tkinter import ttk
# from tkinter import filedialog
# from tkinter import messagebox
# from os import path
# from pprint import pformat
# import webbrowser
# from textwrap import dedent

from templateapp import version
from templateapp import edition

__version__ = version
__edition__ = edition


def get_relative_center_location(parent, width, height):
    """get relative a center location of parent window.

    Parameters
    ----------
    parent (tkinter): tkinter component instance.
    width (int): a width of a child window.
    height (int): a height of a child window..

    Returns
    -------
    tuple: x, y location.
    """
    pwh, px, py = parent.winfo_geometry().split('+')
    px, py = int(px), int(py)
    pw, ph = [int(i) for i in pwh.split('x')]

    x = int(px + (pw - width) / 2)
    y = int(py + (ph - height) / 2)
    return x, y


class Application:
    def __init__(self):
        self._base_title = 'Template GUI'
        self.root = tk.Tk()
        self.root.geometry('800x600+100+100')
        self.root.minsize(200, 200)
        self.root.option_add('*tearOff', False)

    def run(self):
        """Launch template GUI."""
        self.root.mainloop()


def execute():
    """Launch template GUI."""
    app = Application()
    app.run()
