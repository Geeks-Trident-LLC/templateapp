"""Module containing the logic for the Template application."""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from os import path
import webbrowser
from textwrap import dedent
from textwrap import indent
import re
import platform
from pathlib import Path
from pathlib import PurePath
import yaml
from io import StringIO
from textfsm import TextFSM

from pprint import pformat
from dlquery.collection import Tabular

from templateapp import TemplateBuilder

from templateapp import version
from templateapp import edition

__version__ = version
__edition__ = edition


def get_relative_center_location(parent, width, height):
    """get relative a center location of parent window.

    Parameters
    ----------
    parent (tkinter): tkinter widget instance.
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


def set_modal_dialog(dialog):
    """set dialog to become a modal dialog

    Parameters
    ----------
    dialog (tkinter.TK): a dialog or window application.
    """
    dialog.transient(dialog.master)
    dialog.wait_visibility()
    dialog.grab_set()
    dialog.wait_window()


class Data:
    license_name = 'BSD 3-Clause License'
    repo_url = 'https://github.com/Geeks-Trident-LLC/templateapp'
    license_url = path.join(repo_url, 'blob/main/LICENSE')
    # TODO: Need to update wiki page for documentation_url instead of README.md.
    documentation_url = path.join(repo_url, 'blob/develop/README.md')
    copyright_text = 'Copyright @ 2021-2030 Geeks Trident LLC.  All rights reserved.'

    @classmethod
    def get_license(cls):
        license_ = """
            BSD 3-Clause License

            Copyright (c) 2021, Geeks Trident LLC
            All rights reserved.

            Redistribution and use in source and binary forms, with or without
            modification, are permitted provided that the following conditions are met:

            1. Redistributions of source code must retain the above copyright notice, this
               list of conditions and the following disclaimer.

            2. Redistributions in binary form must reproduce the above copyright notice,
               this list of conditions and the following disclaimer in the documentation
               and/or other materials provided with the distribution.

            3. Neither the name of the copyright holder nor the names of its
               contributors may be used to endorse or promote products derived from
               this software without specific prior written permission.

            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
            AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
            IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
            DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
            FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
            DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
            SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
            CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
            OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
            OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        """
        license_ = dedent(license_).strip()
        return license_


class Snapshot(dict):
    """Snapshot for storing data."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for attr, val in self.items():
            if re.match(r'[a-z]\w*$', attr):
                setattr(self, attr, val)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        for attr, val in self.items():
            if re.match(r'[a-z]\w*$', attr):
                setattr(self, attr, val)


class UserTemplate:
    """User template

    Attributes
    ----------
    filename (str): user template file name i.e /home_dir/.templateapp/user_templates.yaml
    status (str): a status message.
    content (str): user template file content.

    Methods
    -------
    is_exist() -> bool
    create(confirmed=True) -> bool
    read() -> str
    search(template_name) -> str
    write(template_name, data) -> str
    """
    def __init__(self):
        self.filename = str(PurePath(Path.home(), '.templateapp', 'user_templates.yaml'))
        self.status = ''
        self.content = ''

    def is_exist(self):
        """return True if /home_dir/.templateapp/user_templates.yaml exists"""
        node = Path(self.filename)
        return node.exists()

    def create(self, confirmed=True):
        """create /home_dir/.templateapp/user_templates.yaml if it IS NOT existed.

        Parameters
        ----------
        confirmed (bool): pop up messagebox for confirmation.

        Returns
        -------
        bool: True or False.
        """
        if self.is_exist():
            return True

        try:
            if confirmed:
                title = 'Creating User Template File'
                yesno = 'Do you want to create {!r} file?'.format(self.filename)
                response = create_msgbox(title=title, yesno=yesno)
            else:
                response = 'yes'

            if response == 'yes':
                node = Path(self.filename)
                parent = node.parent
                if not parent.exists():
                    parent.mkdir(parents=True, exist_ok=True)
                else:
                    if parent.is_file():
                        title = 'Directory Violation'
                        fmt = 'CANT create {!r} file because its parent, {!r}, is a file.'
                        error = fmt.format(str(node), str(parent))
                        create_msgbox(title=title, error=error)
                        return False
                node.touch()
                self.content = node.read_text()
                if confirmed:
                    title = 'Created User Template File'
                    info = '{!r}? is created.'.format(self.filename)
                    create_msgbox(title=title, info=info)
                return True
            else:
                return False
        except Exception as ex:
            title = 'Creating User Template File Issue'
            error = '{}: {}.'.format(type(ex).__name__, ex)
            self.status = error
            create_msgbox(title=title, error=error)

    def read(self):
        """return content of /home_dir/.templateapp/user_templates.yaml"""
        if self.is_exist():
            with open(self.filename) as stream:
                self.content = stream.read()
            return self.content
        else:
            title = 'User Template File Not Found'
            error = "{!r} IS NOT existed.".format(self.filename)
            self.status = error
            create_msgbox(title=title, error=error)
            return ''

    def search(self, template_name):
        """search template via template_name

        Parameters
        ----------
        template_name (str): a template name

        Returns
        -------
        str: a template content
        """
        self.status = ''
        if self.is_exist():
            if not re.match(r'[a-z0-9]+([+._-][a-z0-9]+)*$', template_name):
                title = 'Invalid Template Naming Convention'
                error = 'Template name must be alphanum+[+._-]?alphanum+?[+._-]?alphanum+?'
                self.status = 'INVALID-TEMPLATE-NAME-FORMAT'
                create_msgbox(title=title, error=error)
                return ''

            yaml_obj = yaml.load(self.content, Loader=yaml.SafeLoader)

            if yaml_obj is None:
                yaml_obj = dict()

            if isinstance(yaml_obj, dict):
                if template_name in yaml_obj:
                    self.status = 'FOUND'
                    return yaml_obj.get(template_name)
                else:
                    self.status = 'NOT_FOUND'
                    return ''
            else:
                title = 'Invalid User Template Format'
                error = "{!r} IS NOT correct format.".format(self.filename)
                self.status = 'INVALID-TEMPLATE-FORMAT'
                create_msgbox(title=title, error=error)
                return ''
        else:
            title = 'User Template File Not Found'
            error = "{!r} IS NOT existed.".format(self.filename)
            self.status = error
            create_msgbox(title=title, error=error)
            return ''

    def write(self, template_name, template):
        """store template to /home_dir/.templateapp/user_templates.yaml

        Parameters
        ----------
        template_name (str): a template name
        template (str): a template content

        Returns
        -------
        bool: True if success written, otherwise False.
        """
        self.status = ''
        if self.is_exist():
            self.search(template_name)
            if self.status == 'FOUND' or self.status == 'NOT_FOUND':
                content = self.read()
                yaml_obj = yaml.load(content, Loader=yaml.SafeLoader)
                yaml_obj = yaml_obj or dict()
                if template_name in yaml_obj:
                    title = 'Duplicate Template Name'
                    fmt = ('{!r} template name is already existed.\n'
                           'Do you want to overwrite?')
                    question = fmt.format(template_name)
                    response = create_msgbox(title=title, question=question)
                    if response == 'yes':
                        yaml_obj[template_name] = template
                        for name, tmpl in yaml_obj.items():
                            if tmpl.strip() == template.strip() and name != template_name:
                                title = 'Duplicate Template Name And Content'
                                fmt = ('{!r} template name is a duplicate name and '
                                       'duplicate content with other {!r}.\n  '
                                       'CANT NOT overwrite')
                                error = fmt.format(template_name, name)
                                create_msgbox(title=title, error=error)
                                self.status = 'DUPLICATE-NAME-AND-CONTENT-VIOLATION'
                                return False
                    else:
                        self.status = 'DENIED-OVERWRITE'
                        return False
                else:
                    removed_lst = []
                    for name, tmpl in yaml_obj.items():
                        if tmpl.strip() == template.strip():
                            title = 'Duplicate Template Content'
                            fmt = ('{!r} template name (i.e. your template) has a '
                                   'same content with {!r}.\n  Do you want to rename?')
                            question = fmt.format(template_name, name)
                            response = create_msgbox(title=title, question=question)
                            if response == 'yes':
                                removed_lst.append(name)
                            else:
                                self.status = 'DENIED-RENAME'
                                return False

                    for name in removed_lst:
                        yaml_obj.pop(name)

                    yaml_obj[template_name] = template

                lst = []

                for name in sorted(yaml_obj.keys()):
                    tmpl = yaml_obj.get(name)
                    data = '{}: |-\n{}'.format(name, indent(tmpl, '  '))
                    lst.append(data)

                try:
                    with open(self.filename, 'w') as stream:
                        content = '\n\n'.join(lst)
                        stream.write(content)
                        self.content = content
                        return True
                except Exception as ex:
                    title = 'Writing User Template File Error'
                    error = "{}: {}.".format(type(ex).__name__, ex)
                    self.status = error
                    create_msgbox(title=title, error=error)
                    return False
            else:
                return False


class Application:

    browser = webbrowser

    def __init__(self):
        # support platform: macOS, Linux, and Window
        self.is_macos = platform.system() == 'Darwin'
        self.is_linux = platform.system() == 'Linux'
        self.is_window = platform.system() == 'Windows'

        # standardize tkinter widget for macOS, Linux, and Window operating system
        self.RadioButton = tk.Radiobutton if self.is_linux else ttk.Radiobutton
        self.CheckBox = tk.Checkbutton if self.is_linux else ttk.Checkbutton
        self.Label = ttk.Label
        self.Frame = ttk.Frame
        self.LabelFrame = ttk.LabelFrame
        self.Button = ttk.Button
        self.TextBox = ttk.Entry
        self.TextArea = tk.Text
        self.PanedWindow = ttk.PanedWindow

        self._base_title = 'TemplateApp {}'.format(edition)
        self.root = tk.Tk()
        self.root.geometry('800x600+100+100')
        self.root.minsize(200, 200)
        self.root.option_add('*tearOff', False)

        # tkinter widgets for main layout
        self.panedwindow = None
        self.text_frame = None
        self.entry_frame = None
        self.backup_frame = None
        self.result_frame = None

        self.textarea = None
        self.result_textarea = None

        self.save_as_btn = None
        self.copy_text_btn = None
        self.snippet_btn = None
        self.unittest_btn = None
        self.pytest_btn = None
        self.test_data_btn = None
        self.result_btn = None
        self.store_btn = None
        self.search_chkbox = None

        self.curr_widget = None
        self.prev_widget = None
        self.root.bind_all("<Button-1>", lambda e: self.callback_focus(e))

        # datastore
        self.snapshot = Snapshot()
        self.snapshot.update(user_data='')
        self.snapshot.update(test_data=None)
        self.snapshot.update(result='')
        self.snapshot.update(template='')
        self.snapshot.update(is_built=False)
        self.snapshot.update(switch_app_user_data='')
        self.snapshot.update(switch_app_result_data='')

        # variables
        self.build_btn_var = tk.StringVar()
        self.build_btn_var.set('Build')
        self.test_data_btn_var = tk.StringVar()
        self.test_data_btn_var.set('Test Data')

        # variables: arguments
        self.filename_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.company_var = tk.StringVar()
        self.template_name_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.search_chkbox_var = tk.BooleanVar()

        # variables: app
        self.test_data_chkbox_var = tk.BooleanVar()
        self.template_chkbox_var = tk.BooleanVar()
        self.tabular_chkbox_var = tk.BooleanVar()
        self.tabular_chkbox_var.set(True)

        # method call
        self.set_title()
        self.build_menu()
        self.build_frame()
        self.build_textarea()
        self.build_entry()
        self.build_result()

    def get_template_args(self):
        """return arguments of TemplateBuilder class"""
        result = dict(
            filename=self.filename_var.get(),
            author=self.author_var.get(),
            email=self.email_var.get(),
            company=self.company_var.get(),
            description=self.description_var.get()
        )
        return result

    def set_default_setting(self):
        """reset to default setting"""
        self.filename_var.set('')
        self.author_var.set('')
        self.email_var.set('')
        self.company_var.set('')
        self.description_var.set('')

        self.test_data_chkbox_var.set(False)
        self.template_chkbox_var.set(False)
        self.tabular_chkbox_var.set(True)

    @classmethod
    def get_textarea(cls, widget):
        """Get data from TextArea widget

        Parameters
        ----------
        widget (tk.Text): a tk.Text widget

        Returns
        -------
        str: a text from TextArea widget
        """
        text = widget.get('1.0', 'end')
        last_char = text[-1]
        last_two_chars = text[-2:]
        if last_char == '\r' or last_char == '\n':
            return text[:-1]
        elif last_two_chars == '\r\n':
            return text[:-2]
        else:
            return text

    def set_textarea(self, widget, data, title=''):
        """set data for TextArea widget

        Parameters
        ----------
        widget (tk.Text): a tk.Text widget
        data (any): a data
        title (str): a title of window
        """
        data, title = str(data), str(title).strip()

        curr_state = widget['state']
        widget.configure(state=tk.NORMAL)

        title and self.set_title(title=title)
        widget.delete("1.0", "end")
        widget.insert(tk.INSERT, data)

        widget.configure(state=curr_state)

    def set_title(self, widget=None, title=''):
        """Set a new title for tkinter widget.

        Parameters
        ----------
        widget (tkinter): a tkinter widget.
        title (str): a title.  Default is empty.
        """
        widget = widget or self.root
        btitle = self._base_title
        title = '{} - {}'.format(title, btitle) if title else btitle
        widget.title(title)

    def shift_to_main_app(self):
        """Switch from backup app to main app"""
        user_data = self.snapshot.switch_app_user_data      # noqa
        result_data = self.snapshot.switch_app_result_data  # noqa
        self.snapshot.update(switch_app_user_data='')
        self.snapshot.update(switch_app_result_data='')
        self.set_textarea(self.textarea, user_data)
        self.set_textarea(self.result_textarea, result_data)
        self.panedwindow.remove(self.backup_frame)
        self.panedwindow.insert(1, self.entry_frame)

    def shift_to_backup_app(self):
        """Switch from main app to backup app"""
        self.panedwindow.remove(self.entry_frame)
        self.panedwindow.insert(1, self.backup_frame)

    def callback_focus(self, event):    # noqa
        """Callback for widget selection"""
        widget = self.root.focus_get()
        if widget != self.curr_widget:
            self.prev_widget = self.curr_widget
            self.curr_widget = self.root.focus_get()

    def callback_file_exit(self):
        """Callback for Menu File > Exit."""
        self.root.quit()

    def callback_file_open(self):
        """Callback for Menu File > Open."""
        filetypes = [
            ('Text Files', '.txt', 'TEXT'),
            ('All Files', '*'),
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            with open(filename) as stream:
                content = stream.read()
                self.test_data_btn.config(state=tk.NORMAL)
                self.test_data_btn_var.set('Test Data')
                self.set_textarea(self.result_textarea, '')
                self.snapshot.update(test_data=content)
                self.set_textarea(self.textarea, content, title=filename)

    def callback_help_documentation(self):
        """Callback for Menu Help > Getting Started."""
        self.browser.open_new_tab(Data.documentation_url)

    def callback_help_view_licenses(self):
        """Callback for Menu Help > View Licenses."""
        self.browser.open_new_tab(Data.license_url)

    def callback_help_about(self):
        """Callback for Menu Help > About"""

        def mouse_over(event):  # noqa
            url_lbl.config(font=url_lbl.default_font + ('underline',))
            url_lbl.config(cursor='hand2')

        def mouse_out(event):  # noqa
            url_lbl.config(font=url_lbl.default_font)
            url_lbl.config(cursor='arrow')

        def mouse_press(event):  # noqa
            self.browser.open_new_tab(url_lbl.link)

        about = tk.Toplevel(self.root)
        self.set_title(widget=about, title='About')
        width, height = 440, 400
        x, y = get_relative_center_location(self.root, width, height)
        about.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        about.resizable(False, False)

        top_frame = self.Frame(about)
        top_frame.pack(fill=tk.BOTH, expand=True)

        panedwindow = self.PanedWindow(top_frame, orient=tk.VERTICAL)
        panedwindow.pack(fill=tk.BOTH, expand=True, padx=8, pady=12)

        # company
        frame = self.Frame(panedwindow, width=420, height=20)
        panedwindow.add(frame, weight=1)

        fmt = 'Templateapp v{} ({} Edition)'
        company_lbl = self.Label(frame, text=fmt.format(version, edition))
        company_lbl.pack(side=tk.LEFT)

        # URL
        frame = self.Frame(panedwindow, width=420, height=20)
        panedwindow.add(frame, weight=1)

        url = Data.repo_url
        self.Label(frame, text='URL:').pack(side=tk.LEFT)
        font_size = 12 if self.is_macos else 10
        style = ttk.Style()
        style.configure("Blue.TLabel", foreground="blue")
        url_lbl = self.Label(frame, text=url, font=('sans-serif', font_size))
        url_lbl.config(style='Blue.TLabel')
        url_lbl.default_font = ('sans-serif', font_size)
        url_lbl.pack(side=tk.LEFT)
        url_lbl.link = url

        url_lbl.bind('<Enter>', mouse_over)
        url_lbl.bind('<Leave>', mouse_out)
        url_lbl.bind('<Button-1>', mouse_press)

        # license textbox
        lframe = self.LabelFrame(
            panedwindow, height=300, width=420,
            text=Data.license_name
        )
        panedwindow.add(lframe, weight=7)

        width = 55 if self.is_macos else 48
        height = 19 if self.is_macos else 15 if self.is_linux else 16
        txtbox = self.TextArea(lframe, width=width, height=height, wrap='word')
        txtbox.grid(row=0, column=0, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(lframe, orient=tk.VERTICAL, command=txtbox.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        txtbox.config(yscrollcommand=scrollbar.set)
        txtbox.insert(tk.INSERT, Data.get_license())
        txtbox.config(state=tk.DISABLED)

        # footer - copyright
        frame = self.Frame(panedwindow, width=380, height=20)
        panedwindow.add(frame, weight=1)

        footer = self.Label(frame, text=Data.copyright_text)
        footer.pack(side=tk.LEFT)

        set_modal_dialog(about)

    def callback_preferences_settings(self):
        """Callback for Menu Preferences > Settings"""

        settings = tk.Toplevel(self.root)
        self.set_title(widget=settings, title='Settings')
        width = 520 if self.is_macos else 474 if self.is_linux else 370
        height = 258 if self.is_macos else 242 if self.is_linux else 234
        x, y = get_relative_center_location(self.root, width, height)
        settings.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        settings.resizable(False, False)

        top_frame = self.Frame(settings)
        top_frame.pack(fill=tk.BOTH, expand=True)

        # Settings - Arguments
        lframe_args = self.LabelFrame(
            top_frame, height=100, width=380,
            text='Arguments'
        )
        lframe_args.grid(row=0, column=0, padx=10, pady=(5, 0), sticky=tk.W)

        pady = 0 if self.is_macos else 1

        self.Label(
            lframe_args, text='author'
        ).grid(row=0, column=0, columnspan=2, padx=2, pady=pady, sticky=tk.W+tk.N)
        self.TextBox(
            lframe_args, width=45,
            textvariable=self.author_var
        ).grid(row=0, column=2, columnspan=4, padx=2, pady=pady, sticky=tk.W)

        self.Label(
            lframe_args, text='email'
        ).grid(row=1, column=0, columnspan=2, padx=2, pady=pady, sticky=tk.W+tk.N)
        self.TextBox(
            lframe_args, width=45,
            textvariable=self.email_var
        ).grid(row=1, column=2, columnspan=4, padx=2, pady=pady, sticky=tk.W)

        self.Label(
            lframe_args, text='company'
        ).grid(row=2, column=0, columnspan=2, padx=2, pady=pady, sticky=tk.W+tk.N)
        self.TextBox(
            lframe_args, width=45,
            textvariable=self.company_var
        ).grid(row=2, column=2, columnspan=4, padx=2, pady=pady, sticky=tk.W)

        self.Label(
            lframe_args, text='filename'
        ).grid(row=4, column=0, columnspan=2, padx=2, pady=pady, sticky=tk.W+tk.N)
        self.TextBox(
            lframe_args, width=45,
            textvariable=self.filename_var
        ).grid(row=4, column=2, columnspan=4, padx=2, pady=pady, sticky=tk.W)

        self.Label(
            lframe_args, text='description'
        ).grid(row=5, column=0, columnspan=2, padx=2, pady=pady, sticky=tk.W+tk.N)
        self.TextBox(
            lframe_args, width=45,
            textvariable=self.description_var
        ).grid(row=5, column=2, columnspan=4, padx=2, pady=(pady, 10), sticky=tk.W)

        # Settings - Arguments
        lframe_app = self.LabelFrame(
            top_frame, height=120, width=380,
            text='App'
        )
        lframe_app.grid(row=1, column=0, padx=10, pady=1, sticky=tk.W+tk.N)

        self.CheckBox(
            lframe_app, text='Test Data',
            onvalue=True, offvalue=False,
            variable=self.test_data_chkbox_var
        ).grid(row=0, column=0, padx=2)

        self.CheckBox(
            lframe_app, text='Template',
            onvalue=True, offvalue=False,
            variable=self.template_chkbox_var
        ).grid(row=0, column=1, padx=20)

        self.CheckBox(
            lframe_app, text='Tabular',
            onvalue=True, offvalue=False,
            variable=self.tabular_chkbox_var
        ).grid(row=0, column=2, padx=2)

        # OK and Default buttons
        frame = self.Frame(
            top_frame, height=14, width=380
        )
        frame.grid(row=2, column=0, padx=10, pady=(10, 5), sticky=tk.E+tk.S)

        self.Button(
            frame, text='Default',
            command=lambda: self.set_default_setting(),
        ).grid(row=0, column=6, padx=1, pady=1, sticky=tk.E)

        self.Button(
            frame, text='OK',
            command=lambda: settings.destroy(),
        ).grid(row=0, column=7, padx=1, pady=1, sticky=tk.E)

        set_modal_dialog(settings)

    def build_menu(self):
        """Build menubar for Regex GUI."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file = tk.Menu(menu_bar)
        preferences = tk.Menu(menu_bar)
        help_ = tk.Menu(menu_bar)

        menu_bar.add_cascade(menu=file, label='File')
        menu_bar.add_cascade(menu=preferences, label='Preferences')
        menu_bar.add_cascade(menu=help_, label='Help')

        file.add_command(label='Open', command=lambda: self.callback_file_open())
        file.add_separator()
        file.add_command(label='Quit', command=lambda: self.callback_file_exit())

        preferences.add_command(
            label='Settings',
            command=lambda: self.callback_preferences_settings()
        )
        # preferences.add_separator()

        help_.add_command(label='Documentation',
                          command=lambda: self.callback_help_documentation())
        help_.add_command(label='View Licenses',
                          command=lambda: self.callback_help_view_licenses())
        help_.add_separator()
        help_.add_command(label='About', command=lambda: self.callback_help_about())

    def build_frame(self):
        """Build layout for regex GUI."""
        self.panedwindow = self.PanedWindow(self.root, orient=tk.VERTICAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.text_frame = self.Frame(
            self.panedwindow, width=600, height=300, relief=tk.RIDGE
        )
        self.entry_frame = self.Frame(
            self.panedwindow, width=600, height=10, relief=tk.RIDGE
        )
        self.backup_frame = self.Frame(
            self.panedwindow, width=600, height=10, relief=tk.RIDGE
        )
        self.result_frame = self.Frame(
            self.panedwindow, width=600, height=350, relief=tk.RIDGE
        )
        self.panedwindow.add(self.text_frame, weight=2)
        self.panedwindow.add(self.entry_frame)
        self.panedwindow.add(self.result_frame, weight=7)

    def build_textarea(self):
        """Build input text for regex GUI."""

        self.text_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=1)
        self.textarea = self.TextArea(
            self.text_frame, width=20, height=5, wrap='none',
            name='main_input_textarea',
        )
        self.textarea.grid(row=0, column=0, sticky='nswe')
        vscrollbar = ttk.Scrollbar(
            self.text_frame, orient=tk.VERTICAL, command=self.textarea.yview
        )
        vscrollbar.grid(row=0, column=1, sticky='ns')
        hscrollbar = ttk.Scrollbar(
            self.text_frame, orient=tk.HORIZONTAL, command=self.textarea.xview
        )
        hscrollbar.grid(row=1, column=0, sticky='ew')
        self.textarea.config(
            yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set
        )

    def build_entry(self):
        """Build input entry for regex GUI."""

        def callback_build_btn():
            if self.build_btn_var.get() == 'Build':
                user_data = Application.get_textarea(self.textarea)
                if not user_data:
                    create_msgbox(
                        title='Empty Data',
                        error="Can NOT build regex pattern without data."
                    )
                    return

                try:
                    kwargs = self.get_template_args()
                    factory = TemplateBuilder(user_data=user_data, **kwargs)
                    self.snapshot.update(user_data=user_data)
                    self.snapshot.update(result=factory.template)
                    self.snapshot.update(template=factory.template)
                    self.snapshot.update(is_built=True)
                    self.test_data_btn_var.set('Test Data')
                    self.save_as_btn.config(state=tk.NORMAL)
                    self.copy_text_btn.config(state=tk.NORMAL)
                    self.set_textarea(self.result_textarea, factory.template)
                except Exception as ex:
                    error = '{}: {}'.format(type(ex).__name__, ex)
                    create_msgbox(title='RegexBuilder Error', error=error)

                if self.snapshot.template:  # noqa
                    self.store_btn.config(state=tk.NORMAL)

                if self.snapshot.is_built:  # noqa
                    self.result_btn.config(state=tk.NORMAL)
            else:
                template_name = self.template_name_var.get().strip()
                if template_name:
                    user_template = UserTemplate()
                    template = user_template.search(template_name)
                    self.save_as_btn.config(state=tk.NORMAL)
                    self.copy_text_btn.config(state=tk.NORMAL)
                    self.test_data_btn_var.set('Test Data')
                    if template:
                        self.snapshot.update(template=template)
                        self.snapshot.update(result=template)
                        self.set_textarea(self.result_textarea, template)
                    else:
                        self.snapshot.update(result=user_template.status)
                        self.set_textarea(self.result_textarea, user_template.status)
                else:
                    title = 'Empty Template Name'
                    error = 'CANT retrieve template with empty template name.'
                    create_msgbox(title=title, error=error)

        def callback_save_as_btn():
            filename = filedialog.asksaveasfilename()
            if filename:
                with open(filename, 'w') as stream:
                    content = Application.get_textarea(self.result_textarea)
                    stream.write(content)

        def callback_clear_text_btn():
            prev_widget_name = str(self.prev_widget)
            if prev_widget_name.endswith('.main_template_name_textbox'):
                self.prev_widget.delete(0, tk.END)
            elif prev_widget_name.endswith('.main_result_textarea'):
                title = 'Readonly Window'
                w = 'Result window is READONLY text area.  CAN NOT clear.'
                create_msgbox(title=title, warning=w)
            else:
                self.textarea.delete("1.0", "end")
                self.result_textarea.delete("1.0", "end")
                self.save_as_btn.config(state=tk.DISABLED)
                self.copy_text_btn.config(state=tk.DISABLED)
                self.test_data_btn.config(state=tk.DISABLED)
                self.result_btn.config(state=tk.DISABLED)
                self.store_btn.config(state=tk.DISABLED)

                self.snapshot.update(user_data='')
                self.snapshot.update(test_data=None)
                self.snapshot.update(result='')
                self.snapshot.update(template='')
                self.snapshot.update(is_built=False)

                self.test_data_btn_var.set('Test Data')
                self.build_btn_var.set('Build')
                self.template_name_var.set('')
                self.search_chkbox_var.set(False)
                # self.root.clipboard_clear()
                self.set_title()

        def callback_copy_text_btn():
            content = Application.get_textarea(self.result_textarea)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.root.update()

        def callback_paste_text_btn():
            try:
                data = self.root.clipboard_get()
                if not data:
                    return

                self.test_data_btn.config(state=tk.NORMAL)
                self.test_data_btn_var.set('Test Data')
                self.set_textarea(self.result_textarea, '')
                self.snapshot.update(test_data=data)
                self.snapshot.update(result='')

                title = '<<PASTE - Clipboard>>'
                self.set_textarea(self.textarea, data, title=title)
            except Exception as ex:  # noqa
                create_msgbox(
                    title='Empty Clipboard',
                    info='CAN NOT paste because there is no data in pasteboard.'
                )

        def callback_snippet_btn():
            if self.snapshot.test_data is None:  # noqa
                create_msgbox(
                    title='No Test Data',
                    error=("Can NOT build Python test script without "
                           "test data.\nPlease use Open or Paste button "
                           "to load test data")
                )
                return

            user_data = Application.get_textarea(self.textarea)
            if not user_data:
                create_msgbox(
                    title='Empty Data',
                    error="Can NOT build Python test script without data."
                )
                return

            try:
                kwargs = self.get_template_args()
                factory = TemplateBuilder(
                    user_data=user_data,
                    test_data=self.snapshot.test_data,  # noqa
                    **kwargs
                )
                script = factory.create_python_test()
                self.set_textarea(self.result_textarea, script)
                self.test_data_btn_var.set('Test Data')
                self.snapshot.update(result=script)
                self.save_as_btn.config(state=tk.NORMAL)
                self.copy_text_btn.config(state=tk.NORMAL)
            except Exception as ex:
                error = '{}: {}'.format(type(ex).__name__, ex)
                create_msgbox(title='RegexBuilder Error', error=error)

        def callback_unittest_btn():
            if self.snapshot.test_data is None:  # noqa
                create_msgbox(
                    title='No Test Data',
                    error=("Can NOT build Python Unittest script without "
                           "test data.\nPlease use Open or Paste button "
                           "to load test data")
                )
                return

            user_data = Application.get_textarea(self.textarea)
            if not user_data:
                create_msgbox(
                    title='Empty Data',
                    error="Can NOT build Python Unittest script without data."
                )
                return

            try:
                kwargs = self.get_template_args()
                factory = TemplateBuilder(
                    user_data=user_data,
                    test_data=self.snapshot.test_data,  # noqa
                    **kwargs
                )
                script = factory.create_unittest()
                self.set_textarea(self.result_textarea, script)
                self.test_data_btn_var.set('Test Data')
                self.snapshot.update(result=script)
                self.save_as_btn.config(state=tk.NORMAL)
                self.copy_text_btn.config(state=tk.NORMAL)
            except Exception as ex:
                error = '{}: {}'.format(type(ex).__name__, ex)
                create_msgbox(title='RegexBuilder Error', error=error)

        def callback_pytest_btn():
            if self.snapshot.test_data is None:  # noqa
                create_msgbox(
                    title='No Test Data',
                    error=("Can NOT build Python Pytest script without "
                           "test data.\nPlease use Open or Paste button "
                           "to load test data")
                )
                return

            user_data = Application.get_textarea(self.textarea)
            if not user_data:
                create_msgbox(
                    title='Empty Data',
                    error="Can NOT build Python Pytest script without data."
                )
                return

            try:
                kwargs = self.get_template_args()
                factory = TemplateBuilder(
                    user_data=user_data,
                    test_data=self.snapshot.test_data,  # noqa
                    **kwargs
                )
                script = factory.create_pytest()
                self.set_textarea(self.result_textarea, script)
                self.test_data_btn_var.set('Test Data')
                self.snapshot.update(result=script)
                self.save_as_btn.config(state=tk.NORMAL)
                self.copy_text_btn.config(state=tk.NORMAL)
            except Exception as ex:
                error = '{}: {}'.format(type(ex).__name__, ex)
                create_msgbox(title='RegexBuilder Error', error=error)

        def callback_test_data_btn():
            if self.snapshot.test_data is None:  # noqa
                create_msgbox(
                    title='No Test Data',
                    error="Please use Open or Paste button to load test data"
                )
                return

            name = self.test_data_btn_var.get()
            if name == 'Test Data':
                self.test_data_btn_var.set('Hide')
                self.set_textarea(
                    self.result_textarea,
                    self.snapshot.test_data  # noqa
                )
            else:
                self.test_data_btn_var.set('Test Data')
                self.set_textarea(
                    self.result_textarea,
                    self.snapshot.result  # noqa
                )

        def callback_result_btn():
            if self.snapshot.test_data is None:  # noqa
                create_msgbox(
                    title='No Test Data',
                    error=("Can NOT parse text without "
                           "test data.\nPlease use Open or Paste button "
                           "to load test data")
                )
                return

            user_data = Application.get_textarea(self.textarea)
            if not user_data:
                create_msgbox(
                    title='Empty Data',
                    error="Can NOT build regex pattern without data."
                )
                return

            try:
                kwargs = self.get_template_args()
                factory = TemplateBuilder(user_data=user_data, **kwargs)
                self.snapshot.update(user_data=user_data)
                self.snapshot.update(template=factory.template)
                self.snapshot.update(is_built=True)
                stream = StringIO(factory.template)  # noqa
                parser = TextFSM(stream)
                rows = parser.ParseTextToDicts(self.snapshot.test_data)  # noqa

                result = ''
                test_data = self.snapshot.test_data  # noqa
                template = factory.template
                fmt = '\n\n<<{}>>\n\n{{}}'.format('=' * 20)

                if self.template_chkbox_var.get() and template:
                    result += fmt.format(template) if result else template

                if self.test_data_chkbox_var.get() and test_data:  # noqa
                    result += fmt.format(test_data) if result else test_data

                if self.tabular_chkbox_var.get():
                    tabular_obj = Tabular(rows)
                    tabular_data = tabular_obj.get()
                    result += fmt.format(tabular_data) if result else tabular_data
                else:
                    pretty_data = pformat(rows)
                    result += fmt.format(pretty_data) if result else pretty_data

                self.test_data_btn_var.set('Test Data')
                self.snapshot.update(result=result)
                self.set_textarea(self.result_textarea, result)
            except Exception as ex:
                error = '{}: {}'.format(type(ex).__name__, ex)
                create_msgbox(title='RegexBuilder Error', error=error)

        def callback_store_btn():
            user_template = UserTemplate()
            if not user_template.is_exist():
                title = 'User Template File Not Found'
                fmt = ('The feature is only available when {!r} is existed.\n'
                       'Do you want to create this file?')
                question = fmt.format(user_template.filename)
                response = create_msgbox(title=title, question=question)
                if response == 'no':
                    return
                else:
                    user_template.create(confirmed=False)

            if user_template.is_exist():
                user_data = self.get_textarea(self.textarea)
                result_data = self.get_textarea(self.result_textarea)
                self.snapshot.update(switch_app_user_data=user_data)
                self.snapshot.update(switch_app_result_data=result_data)

                self.set_textarea(self.textarea, result_data)
                self.set_textarea(self.result_textarea, user_template.read())
                self.shift_to_backup_app()

        def callback_search_chkbox():
            user_template = UserTemplate()
            if not user_template.is_exist():
                title = 'User Template File Not Found'
                fmt = 'The feature is only available when {!r} is existed.'
                info = fmt.format(user_template.filename)
                create_msgbox(title=title, info=info)
                self.search_chkbox_var.set(False)
                return

            if self.search_chkbox_var.get():
                self.build_btn_var.set('Search')
                self.store_btn.config(state=tk.DISABLED)
            else:
                self.build_btn_var.set('Build')
                if self.snapshot.is_built:  # noqa
                    self.store_btn.config(state=tk.NORMAL)

        def callback_app_backup_refresh_btn():
            user_data = self.snapshot.switch_app_user_data      # noqa
            try:
                kwargs = self.get_template_args()
                factory = TemplateBuilder(user_data=user_data, **kwargs)
                self.set_textarea(self.textarea, factory.template)
            except Exception as ex:
                error = '{}: {}'.format(type(ex).__name__, ex)
                create_msgbox(title='RegexBuilder Error', error=error)

        def callback_app_backup_save_btn():
            user_template = UserTemplate()
            tmpl_name = self.template_name_var.get()
            status = user_template.status
            is_invalid_format = status == 'INVALID-TEMPLATE-FORMAT'
            is_invalid_name = status == 'INVALID-TEMPLATE-NAME-FORMAT'

            if is_invalid_name or is_invalid_format:
                return
            elif status == 'FOUND':
                title = 'Duplicate Template Name'
                fmt = ('{!r} template name is already existed.  '
                       'Please use different name.')
                info = fmt.format(tmpl_name)
                create_msgbox(title=title, info=info)
                return

            user_data = self.get_textarea(self.textarea)
            user_template.write(tmpl_name, user_data.strip())

            self.set_textarea(self.result_textarea, user_template.content)

        # def callback_rf_btn():
        #     create_msgbox(
        #         title='Robotframework feature',
        #         info="Robotframework button is available in Pro or Enterprise Edition."
        #     )

        # customize width for buttons
        btn_width = 6 if self.is_macos else 8
        # open button
        open_file_btn = self.Button(
            self.entry_frame, text='Open',
            name='main_open_btn',
            command=self.callback_file_open,
            width=btn_width
        )
        open_file_btn.grid(row=0, column=0, padx=(2, 0), pady=(2, 0))

        # Save As button
        self.save_as_btn = self.Button(
            self.entry_frame, text='Save As',
            name='main_save_as_btn',
            state=tk.DISABLED,
            command=callback_save_as_btn,
            width=btn_width
        )
        self.save_as_btn.grid(row=0, column=1, pady=(2, 0))

        # customize width for buttons
        btn_width = 5.5 if self.is_macos else 8
        # copy button
        self.copy_text_btn = self.Button(
            self.entry_frame, text='Copy',
            name='main_copy_btn',
            state=tk.DISABLED,
            command=callback_copy_text_btn,
            width=btn_width
        )
        self.copy_text_btn.grid(row=0, column=2, pady=(2, 0))

        # paste button
        paste_text_btn = ttk.Button(
            self.entry_frame, text='Paste',
            name='main_paste_btn',
            command=callback_paste_text_btn,
            width=btn_width
        )
        paste_text_btn.grid(row=0, column=3, pady=(2, 0))

        # clear button
        clear_text_btn = self.Button(
            self.entry_frame, text='Clear',
            name='main_clear_btn',
            command=callback_clear_text_btn,
            width=btn_width
        )
        clear_text_btn.grid(row=0, column=4, pady=(2, 0))

        # build button
        build_btn = self.Button(
            self.entry_frame,
            textvariable=self.build_btn_var,
            name='main_build_btn',
            command=callback_build_btn,
            width=btn_width
        )
        build_btn.grid(row=0, column=5, pady=(2, 0))

        # snippet button
        self.snippet_btn = self.Button(
            self.entry_frame, text='Snippet',
            name='main_snippet_btn',
            command=callback_snippet_btn,
            width=btn_width
        )
        self.snippet_btn.grid(row=0, column=6, pady=(2, 0))

        # unittest button
        self.unittest_btn = self.Button(
            self.entry_frame, text='Unittest',
            name='main_unittest_btn',
            command=callback_unittest_btn,
            width=btn_width
        )
        self.unittest_btn.grid(row=0, column=7, pady=(2, 0))

        # pytest button
        self.pytest_btn = self.Button(
            self.entry_frame, text='Pytest',
            name='main_pytest_btn',
            command=callback_pytest_btn,
            width=btn_width
        )
        self.pytest_btn.grid(row=0, column=8, pady=(2, 0))

        # test_data button
        self.test_data_btn = self.Button(
            self.entry_frame,
            name='main_test_data_btn',
            state=tk.DISABLED,
            command=callback_test_data_btn,
            textvariable=self.test_data_btn_var,
            width=btn_width
        )
        self.test_data_btn.grid(row=0, column=9, pady=(2, 0))

        # customize width for buttons
        btn_width = 6 if self.is_macos else 8
        # result button
        self.result_btn = self.Button(
            self.entry_frame, text='Result',
            name='main_result_btn',
            state=tk.DISABLED,
            command=callback_result_btn,
            width=btn_width
        )
        self.result_btn.grid(row=1, column=0, padx=(2, 0), pady=(0, 2))

        # store button
        self.store_btn = self.Button(
            self.entry_frame, text='Store',
            name='main_store_btn',
            state=tk.DISABLED,
            command=callback_store_btn,
            width=btn_width
        )
        self.store_btn.grid(row=1, column=1, pady=(0, 2))

        # frame container for checkbox and textbox
        frame = self.Frame(self.entry_frame)
        frame.grid(row=1, column=2, pady=(0, 2), columnspan=8, sticky=tk.W)

        # customize x padding for search checkbox
        x = 0 if self.is_macos else 6 if self.is_linux else 2
        # search checkbox
        self.search_chkbox = self.CheckBox(
            frame, text='search',
            name='main_search_checkbox',
            variable=self.search_chkbox_var,
            onvalue=True, offvalue=False,
            command=callback_search_chkbox
        )
        self.search_chkbox.grid(row=0, column=0, padx=(0, x), sticky=tk.W)

        # template name textbox
        self.TextBox(
            frame, width=50,
            name='main_template_name_textbox',
            textvariable=self.template_name_var
        ).grid(row=0, column=1, sticky=tk.W)

        # Robotframework button
        # rf_btn = self.Button(self.entry_frame, text='RF',
        #                     command=callback_rf_btn, width=4)
        # rf_btn.grid(row=0, column=10)

        # backup app
        self.Label(
            self.backup_frame, text='Author'
        ).grid(row=0, column=0, padx=(4, 1), pady=(4, 0), sticky=tk.W)

        frame = self.Frame(self.backup_frame)
        frame.grid(row=0, column=1, padx=(1, 2), pady=(4, 0), sticky=tk.W)

        # customize width for author textbox
        width = 18 if self.is_macos else 20 if self.is_linux else 28
        self.TextBox(
            frame, width=width,
            textvariable=self.author_var
        ).grid(row=0, column=0, sticky=tk.W)

        # customize x-padding for email label
        x = 6 if self.is_macos else 7 if self.is_linux else 4
        self.Label(
            frame, text='Email'
        ).grid(row=0, column=1, padx=(x, 2), sticky=tk.W)

        # customize width for email textbox
        width = 27 if self.is_macos else 32 if self.is_linux else 43
        self.TextBox(
            frame, width=width,
            textvariable=self.email_var
        ).grid(row=0, column=2, sticky=tk.W)

        # customize x-padding for company label
        x = 5 if self.is_macos else 6 if self.is_linux else 5
        self.Label(
            frame, text='Company'
        ).grid(row=0, column=3, padx=(x, 2), sticky=tk.W)

        # customize width for company textbox
        width = 18 if self.is_macos else 20 if self.is_linux else 28
        self.TextBox(
            frame, width=width,
            textvariable=self.company_var
        ).grid(row=0, column=4, sticky=tk.W)

        # custom pady for description
        pady = 0 if self.is_macos else 1
        self.Label(
            self.backup_frame, text='Description'
        ).grid(row=1, column=0, padx=(4, 1), pady=pady, sticky=tk.W)

        # custom width for description textbox
        width = 78 if self.is_macos else 88 if self.is_linux else 118
        self.TextBox(
            self.backup_frame, width=width,
            textvariable=self.description_var
        ).grid(row=1, column=1, padx=(1, 2), pady=pady, sticky=tk.W)

        self.Label(
            self.backup_frame, text='Name'
        ).grid(row=2, column=0, padx=(4, 1), pady=(0, 2), sticky=tk.W)

        frame = self.Frame(
            self.backup_frame
        )
        frame.grid(row=2, column=1, padx=(1, 2), pady=(0, 2), sticky=tk.W)

        # customize width for template name textbox
        width = 48 if self.is_macos else 50 if self.is_linux else 70
        self.TextBox(
            frame, width=width,
            textvariable=self.template_name_var
        ).pack(side=tk.LEFT)
        self.Button(
            frame, text='Refresh',
            command=callback_app_backup_refresh_btn,
            width=btn_width
        ).pack(side=tk.LEFT)
        self.Button(
            frame, text='Save',
            command=callback_app_backup_save_btn,
            width=btn_width
        ).pack(side=tk.LEFT)
        self.Button(
            frame, text='Close',
            command=self.shift_to_main_app,
            width=btn_width
        ).pack(side=tk.LEFT)

    def build_result(self):
        """Build result text"""
        self.result_frame.rowconfigure(0, weight=1)
        self.result_frame.columnconfigure(0, weight=1)
        self.result_textarea = self.TextArea(
            self.result_frame, width=20, height=5, wrap='none',
            name='main_result_textarea'
        )
        self.result_textarea.grid(row=0, column=0, sticky='nswe')
        vscrollbar = ttk.Scrollbar(
            self.result_frame, orient=tk.VERTICAL,
            command=self.result_textarea.yview
        )
        vscrollbar.grid(row=0, column=1, sticky='ns')
        hscrollbar = ttk.Scrollbar(
            self.result_frame, orient=tk.HORIZONTAL,
            command=self.result_textarea.xview
        )
        hscrollbar.grid(row=1, column=0, sticky='ew')
        self.result_textarea.config(
            yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set
        )

    def run(self):
        """Launch template GUI."""
        self.root.mainloop()


def execute():
    """Launch template GUI."""
    app = Application()
    app.run()
