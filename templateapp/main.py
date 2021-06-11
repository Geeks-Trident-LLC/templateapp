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
    options (argparse.Namespace): a argparse.Namespace instance.

    Returns
    -------
    None: will invoke ``templateapp.Application().run()`` and ``sys.exit(0)``
    if end user requests `--gui`
    """
    if options.gui:
        app = Application()
        app.run()
        sys.exit(0)


class Cli:
    """templateapp console CLI application."""

    def __init__(self):
        self.filename = ''
        self.filetype = ''
        self.result = None

        parser = argparse.ArgumentParser(
            prog='templateapp',
            usage='%(prog)s [options]',
            description='%(prog)s application',
        )

        parser.add_argument(
            '--gui', action='store_true',
            help='launch a template GUI application'
        )

        self.parser = parser

    def validate_cli_flags(self, options):
        """Validate argparse `options`.

        Parameters
        ----------
        options (argparse.Namespace): a argparse.Namespace instance.

        Returns
        -------
        bool: show ``self.parser.print_help()`` and call ``sys.exit(1)`` if
        all flags are empty or False, otherwise, return True
        """

        chk = any(bool(i) for i in vars(options).values())

        if not chk:
            self.parser.print_help()
            sys.exit(1)

        return True

    def run(self):
        """Take CLI arguments, parse it, and process."""
        options = self.parser.parse_args()
        self.validate_cli_flags(options)
        run_gui_application(options)


def execute():
    """Execute template console CLI."""
    app = Cli()
    app.run()
