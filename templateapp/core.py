"""Module containing the logic for template builder."""

import re

from regexapp import LinePattern

from templateapp.exceptions import TemplateParsedLineError


class ParsedLine:
    """Parse line to template format

    Attributes
    ----------
    text (str): a data.
    line (str): a line data.
    template_op (str): template operator.
    ignore_case (bool): a case insensitive flag.
    variables (list): a list of variables.

    Properties
    ----------
    is_empty (bool): True if a line doesnt have data, otherwise False.
    is_a_word (bool): True if text is a single word, otherwise False.
    is_not_containing_letter (bool): True if line is not containing any letter,
            otherwise, False.

    Methods
    -------
    build() -> None
    get_statement() -> str

    Raises
    -------
    TemplateParsedLineError: raise exception if there is invalid format for parsing.
    """
    def __init__(self, text):
        self.text = str(text)
        self.line = ''
        self.template_op = ''
        self.ignore_case = False
        self.variables = list()
        self.build()

    @property
    def is_empty(self):
        """return True if a line is empty"""
        return not bool(self.line.strip())

    @property
    def is_a_word(self):
        """return True if text is a single word"""
        return bool(re.match(r'[a-z]\w+$', self.text.rstrip(), re.I))

    @property
    def is_not_containing_letter(self):
        """return True if a line doesn't contain any alphanum"""
        if self.is_empty:
            return False

        return bool(re.match(r'[^a-z0-9]+$', self.line, re.I))

    def get_statement(self):
        """return a statement for building template

        Returns
        -------
        str: a statement for template
        """
        if self.is_empty:
            return ''

        if self.is_a_word:
            return self.text

        pat_obj = LinePattern(self.line, ignore_case=self.ignore_case)

        if pat_obj.variables:
            self.variables = pat_obj.variables[:]
            statement = pat_obj.statement
        else:
            try:
                re.compile(self.line)
                if re.search(r'\s', self.line):
                    statement = pat_obj
                else:
                    statement = self.line
            except Exception as ex:     # noqa
                statement = pat_obj

        statement = statement.replace('(?i)^', '^(?i)')
        spacer = '  ' if statement.startswith('^') else '  ^'
        statement = '{}{}'.format(spacer, statement)
        if statement.endswith('$'):
            statement = '{}$'.format(statement)
        if self.template_op:
            statement = '{} -> {}'.format(statement, self.template_op)
        return statement

    def build(self):
        """parse line to reapply for building template"""
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
