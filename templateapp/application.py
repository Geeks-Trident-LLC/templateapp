"""Module containing the logic for the Template application."""

import tkinter as tk
# from tkinter import ttk
# from tkinter import filedialog
from tkinter import messagebox
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


def create_msgbox(title=None, error=None, warning=None, info=None,
                  question=None, okcancel=None, retrycancel=None,
                  yesno=None, yesnocancel=None, **options):
    """create tkinter.messagebox
    Parameters
    ----------
    title (str): a title of messagebox.  Default is None.
    error (str): an error message.  Default is None.
    warning (str): a warning message. Default is None.
    info (str): an information message.  Default is None.
    question (str): a question message.  Default is None.
    okcancel (str): an ok or cancel message.  Default is None.
    retrycancel (str): a retry or cancel message.  Default is None.
    yesno (str): a yes or no message.  Default is None.
    yesnocancel (str): a yes, no, or cancel message.  Default is None.
    options (dict): options for messagebox.

    Returns
    -------
    any: a string or boolean result
    """
    if error:
        # a return result is a "ok" string
        result = messagebox.showerror(title=title, message=error, **options)
    elif warning:
        # a return result is a "ok" string
        result = messagebox.showwarning(title=title, message=warning, **options)
    elif info:
        # a return result is a "ok" string
        result = messagebox.showinfo(title=title, message=info, **options)
    elif question:
        # a return result is a "yes" or "no" string
        result = messagebox.askquestion(title=title, message=question, **options)
    elif okcancel:
        # a return result is boolean
        result = messagebox.askokcancel(title=title, message=okcancel, **options)
    elif retrycancel:
        # a return result is boolean
        result = messagebox.askretrycancel(title=title, message=retrycancel, **options)
    elif yesno:
        # a return result is boolean
        result = messagebox.askyesno(title=title, message=yesno, **options)
    elif yesnocancel:
        # a return result is boolean or None
        result = messagebox.askyesnocancel(title=title, message=yesnocancel, **options)
    else:
        # a return result is a "ok" string
        result = messagebox.showinfo(title=title, message=info, **options)

    return result


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
