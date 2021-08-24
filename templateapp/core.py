"""Module containing the logic for template builder."""

import re


from templateapp.exceptions import TemplateParsedLineError


class ParsedLine:
    """

    Attributes
    ----------
    text (str): a data.
    line (str): a line data.
    template_op (str): template operator.
    ignore_case (bool): a case insensitive flag.

    Properties
    ----------
    is_empty (bool): True if a line doesnt have data, otherwise False.
    has_template_op (bool): True if line has template operator, otherwise False.
    is_ignore_case (bool): True if a line need case insensitive flag.

    Methods
    -------
    build() -> None

    Raises
    -------
    TemplateParsedLineError: raise exception if there is invalid format for parsing.
    """
    def __init__(self, text):
        self.text = str(text)
        self.line = ''
        self.template_op = ''
        self.ignore_case = False
        self.build()

    @property
    def is_empty(self):
        return not bool(self.line)

    @property
    def has_template_op(self):
        return bool(self.template_op)

    @property
    def is_ignore_case(self):
        return self.ignore_case

    def build(self):

        lst = self.text.rsplit(' -> ', 1)
        if len(lst) == 2:
            self.template_op = lst[-1].strip()
            text = lst[0].rstrip()
        else:
            text = self.text

        pat = r'(?P<ic>ignore_case )?(?P<line>.*)'
        match = re.match(pat, text, re.I)
        if match:
            self.ignore_case = bool(match.groupdict().get('ic'))
            line = match.groupdict().get('line')
            self.line = line or ''
        else:
            error = 'Invalid format - {!r}'.format(self.text)
            raise TemplateParsedLineError(error)
