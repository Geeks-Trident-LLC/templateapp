"""Module containing the logic for template builder."""

import re
from datetime import datetime
from textwrap import indent
from textfsm import TextFSM
from io import StringIO
from pprint import pformat
from textwrap import dedent

from regexapp import LinePattern
from regexapp.core import enclose_string

from templateapp.exceptions import TemplateParsedLineError
from templateapp.exceptions import TemplateBuilderError
from templateapp.config import edition

import logging
logger = logging.getLogger(__file__)


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


class TemplateBuilder:
    """Create template and test script

    Attributes
    ----------
    test_data (str): a test data.
    user_data (str): a user data.
    namespace (str): a reference name for template datastore.
    author (str): author name.  Default is empty.
    email (str): author email.  Default is empty.
    company (str): company name.  Default is empty.
    description (str): a description about template.  Default is empty.
    other_options (dict): other options for Pro or Enterprise edition.

    Methods
    -------
    TemplateBuilder.convert_to_string(data) -> str
    prepare() -> None
    build_template_comment() -> None
    build() -> None
    show_debug_info(test_result=None, expected_result=None) -> None
    verify(expected_rows_count=None, expected_result=None, debug=False) -> bool
    create_unittest_script() -> str
    create_pytest_script() -> str
    create_snippet_script() -> str

    Raises
    ------
    TemplateBuilderError: will raise exception if a created template is invalid.
    """
    logger = logger

    def __init__(self, test_data='', user_data='', namespace='',
                 author='', email='', company='', description='',
                 **other_options):
        self.test_data = TemplateBuilder.convert_to_string(test_data)
        self.user_data = TemplateBuilder.convert_to_string(user_data)
        self.namespace = str(namespace)
        self.author = str(author)
        self.email = str(email)
        self.company = str(company)
        self.description = TemplateBuilder.convert_to_string(description)
        self.other_options = other_options
        self.variables = []
        self.statements = []
        self.template = ''
        self.template_parser = None
        self.result = None
        self.verified_message = ''

        self.build()

    @classmethod
    def convert_to_string(cls, data):
        """convert data to string

        Parameters
        ----------
        data (str, list): a data

        Returns
        -------
        str: a text
        """
        if isinstance(data, list):
            return '\n'.join(str(item) for item in data)
        else:
            return str(data)

    def prepare(self):
        """prepare data to build template"""
        for line in self.user_data.splitlines():
            line = line.rstrip()

            parsed_line = ParsedLine(line)
            statement = parsed_line.get_statement()

            if statement:
                self.statements.append(statement)
            else:
                self.statements and self.statements.append(statement)

            if parsed_line.variables:
                for v in parsed_line.variables:
                    v not in self.variables and self.variables.append(v)

    def build_template_comment(self):
        """return a template comment including created by, email, company,
        created date, and description"""

        fmt = '# Template is generated by templateapp {} Edition'
        fmt1 = '# Created by  : {}'
        fmt2 = '# Email       : {}'
        fmt3 = '# Company     : {}'
        fmt4 = '# Created date: {:%Y-%m-%d}'
        fmt5 = '# Description : {}'

        author = self.author or self.company
        lst = ['#' * 80, fmt.format(edition)]
        author and lst.append(fmt1.format(author))
        self.email and lst.append(fmt2.format(self.email))
        self.company and lst.append(fmt3.format(self.company))
        lst.append(fmt4.format(datetime.now()))
        if self.description:
            description = indent(self.description, '#     ').strip('# ')
            lst.append(fmt5.format(description))
        lst.append('#' * 80)
        return '\n'.join(lst)

    def build(self):
        """build template

        Raises
        ------
        TemplateBuilderError: will raise exception if a created template is invalid.
        """
        self.template = ''
        self.prepare()
        if self.variables:
            comment = self.build_template_comment()
            variables = '\n'.join(v.value for v in self.variables)
            template_definition = '\n'.join(self.statements)
            if not template_definition.strip().startswith('Start'):
                template_definition = 'Start\n{}'.format(template_definition)
            fmt = '{}\n{}\n\n{}'
            self.template = fmt.format(comment, variables, template_definition)

            try:
                stream = StringIO(self.template)
                self.template_parser = TextFSM(stream)
            except Exception as ex:
                error = '{}: {}'.format(type(ex).__name__, ex)
                raise TemplateBuilderError(error)
        else:
            raise Exception()

    def show_debug_info(self, test_result=None, expected_result=None):
        """show debug information
        
        Parameters
        ----------
        test_result (list): a list of dictionary.
        expected_result (list): a list of dictionary.
        """
        if self.verified_message:
            lst = [
                '*** {}'.format(self.verified_message),
                '==' * 40,
                'Template:',
                '---------',
                self.template,
                'Test data:',
                '----------',
                self.test_data,
            ]
            if test_result is not None and expected_result is not None:
                lst += [
                    'Expected result:',
                    '------------',
                    pformat(expected_result),
                    'Test result:',
                    '------------',
                    pformat(test_result)
                ]
            msg = '\n'.join(lst) + '\n'
            self.logger.debug(msg)

    def verify(self, expected_rows_count=None, expected_result=None, debug=False):
        """verify test_data via template
        
        Parameters
        ----------
        expected_rows_count (int): total number of rows.
        expected_result (list): a list of dictionary.
        debug (bool): True will show debug info.  Default is False.

        Returns
        -------
        bool: True if it is verified, otherwise False.

        Raises
        ------
        TemplateBuilderError: show exception if there is error during parsing text.
        """
        if not self.test_data:
            self.verified_message = 'test_data is empty.'
            debug and self.show_debug_info()
            return False

        is_verified = True
        try:
            rows = self.template_parser.ParseTextToDicts(self.test_data)
            if not rows:
                self.verified_message = 'There is no record after parsed.'
                debug and self.show_debug_info()
                return False

            if expected_rows_count is not None:
                rows_count = len(rows)
                chk = expected_rows_count == rows_count
                is_verified &= chk
                if not chk:
                    fmt = 'Total parsed rows is {} while expected rows is {}.'
                    self.verified_message = fmt.format(rows_count, expected_rows_count)

            if expected_result is not None:
                chk = rows == expected_result
                is_verified &= chk
                if not chk:
                    msg = 'Parsed result is as same as expected result.'
                    if self.verified_message:
                        self.verified_message += '\n{}'.format(msg)
                    else:
                        self.verified_message = msg

            if not is_verified and debug:
                self.show_debug_info(test_result=rows, expected_result=expected_result)

            return is_verified

        except Exception as ex:
            error = '{}: {}'.format(type(ex).__name__, ex)
            raise TemplateBuilderError(error)

    def create_unittest(self):
        """return a Python unittest script

        Raises
        ------
        TemplateBuilderError: raise exception if test_data is empty.
        """

        if not self.test_data:
            error = 'CANT create Python unittest script without test data.'
            raise TemplateBuilderError(error)

        fmt = """
            {docstring}
            
            import unittest
            from textfsm import TextFSM
            from io import StringIO
            
            template = r{template}
            
            test_data = {test_data}
            
            
            class TestTemplate(unittest.TestCase):
                def test_textfsm_template(self):
                    stream = StringIO(template)
                    parser = TextFSM(stream)
                    rows = parser.ParseTextToDicts(test_data)
                    total_rows_count = len(rows)
                    self.assertGreaterEqual(total_rows_count, 0)
        """
        fmt = dedent(fmt).strip()

        docstring = ('Python unittest script is generated by '
                     'templateapp {} Edition').format(edition)
        script = fmt.format(
            docstring='"""{}"""'.format(docstring),
            template=enclose_string(self.template),
            test_data=enclose_string(self.test_data)
        )

        return script

    def create_pytest(self):
        """return a Python pytest script

        Raises
        ------
        TemplateBuilderError: raise exception if test_data is empty.
        """

        if not self.test_data:
            error = 'CANT create Python pytest script without test data.'
            raise TemplateBuilderError(error)

        fmt = """
            {docstring}

            from textfsm import TextFSM
            from io import StringIO

            template = r{template}
            
            test_data = {test_data}


            class TestTemplate:
                def test_textfsm_template(self):
                    stream = StringIO(template)
                    parser = TextFSM(stream)
                    rows = parser.ParseTextToDicts(test_data)
                    total_rows_count = len(rows)
                    assert total_rows_count > 0
        """

        fmt = dedent(fmt).strip()

        docstring = ('Python pytest script is generated by '
                     'templateapp {} edition').format(edition)
        script = fmt.format(
            docstring='"""{}"""'.format(docstring),
            template=enclose_string(self.template),
            test_data=enclose_string(self.test_data)
        )

        return script

    def create_python_test(self):
        """return a Python snippet script

        Raises
        ------
        TemplateBuilderError: raise exception if test_data is empty.
        """

        if not self.test_data:
            error = 'CANT create Python snippet script without test data.'
            raise TemplateBuilderError(error)

        fmt = r'''
            {docstring}

            from textfsm import TextFSM
            from io import StringIO
            from pprint import pformat

            template = r{template}

            test_data = {test_data}


            def test_textfsm_template(template_, test_data_):
                """test textfsm template via test data
                
                Parameters
                ----------
                template_ (str): a content of textfsm template.
                test_data_ (str): test data.
                """
                
                # show test data
                print("Test data:\n----------\n%s" % test_data_)
                print("\n%s\n" % ("+" * 40))
                
                # show textfms template
                print("Template:\n---------\n%s" % template_)
                
                stream = StringIO(template_)
                parser = TextFSM(stream)
                rows = parser.ParseTextToDicts(test_data_)
                total_rows_count = len(rows)
                assert total_rows_count > 0
                
                # print parsed result
                print("\n%s\n" % ("+" * 40))
                print("Result:\n-------\n%s\n" % pformat(rows))
            
            # function call
            test_textfsm_template(template, test_data)
        '''

        fmt = dedent(fmt).strip()

        docstring = ('Python snippet script is generated by '
                     'templateapp {} edition').format(edition)
        script = fmt.format(
            docstring='"""{}"""'.format(docstring),
            template=enclose_string(self.template),
            test_data=enclose_string(self.test_data)
        )

        return script
