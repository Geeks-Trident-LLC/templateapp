"""Module containing the logic for the templateapp entry-points."""

import sys
import argparse
# from os import path
# from textwrap import dedent
from templateapp.application import Application


def run_gui_application(options):
    """Run templateapp GUI application.

    Parameters
    ----------
    options (argparse.Namespace): argparse.Namespace instance.

    Returns
    -------
    None: will invoke ``templateapp.Application().run()`` and ``sys.exit(0)``
    if end user requests `--gui`
    """
    if options.gui:
        app = Application()
        app.run()
        sys.exit(0)


def show_dependency(options):
    if options.dependency:
        from platform import uname, python_version
        from templateapp.config import Data
        lst = [
            Data.main_app_text,
            'Platform: {0.system} {0.release} - Python {1}'.format(
                uname(), python_version()
            ),
            '--------------------',
            'Dependencies:'
        ]

        for pkg in Data.get_dependency().values():
            lst.append('  + Package: {0[package]}'.format(pkg))
            lst.append('             {0[url]}'.format(pkg))

        width = max(len(item) for item in lst)
        txt = '\n'.join('| {1:{0}} |'.format(width, item) for item in lst)
        print('+-{0}-+\n{1}\n+-{0}-+'.format(width * '-', txt))
        sys.exit(0)


class Cli:
    """templateapp console CLI application."""

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog='templateapp',
            usage='%(prog)s [options]',
            description='%(prog)s application',
        )

        parser.add_argument(
            '--gui', action='store_true',
            help='launch a template GUI application'
        )

        parser.add_argument(
            '-d', '--dependency', action='store_true',
            help='Show TemplateApp dependent package(s).'
        )

        self.parser = parser
        self.options = self.parser.parse_args()

    def validate_cli_flags(self):
        """Validate argparse `options`.

        Returns
        -------
        bool: show ``self.parser.print_help()`` and call ``sys.exit(1)`` if
        all flags are empty or False, otherwise, return True
        """

        chk = any(bool(i) for i in vars(self.options).values())

        if not chk:
            self.parser.print_help()
            sys.exit(1)

        return True

    def run(self):
        """Take CLI arguments, parse it, and process."""
        show_dependency(self.options)
        self.validate_cli_flags()
        run_gui_application(self.options)


def execute():
    """Execute template console CLI."""
    app = Cli()
    app.run()
