import pytest
from textwrap import dedent
from datetime import datetime
from pathlib import Path, PurePath

from templateapp import ParsedLine
from templateapp import TemplateBuilder


@pytest.fixture
def tc_info():
    class TestInfo:
        pass

    test_info = TestInfo()
    dt_str = format(datetime.now(), '%Y-%m-%d')

    test_data = """
        Title                   Price       Genre
        XML Developer's Guide   44.95       Computer
        Midnight Rain           5.95        Fantasy
        Maeve Ascendant         5.95        Fantasy
    """

    user_data = """
        Title                   Price       Genre
        mixed_words(var_title)   number(var_price)   words(var_genre) -> Record
    """

    template = """
        ################################################################################
        # Template is generated by templateapp Community Edition
        # Created by  : user1
        # Email       : user1@abcxyz.com
        # Company     : ABC XYZ LLC
        # Created date: _datetime_
        ################################################################################
        Value title (\\S*[a-zA-Z0-9]\\S*( \\S*[a-zA-Z0-9]\\S*)*)
        Value price ((\\d+)?[.]?\\d+)
        Value genre ([a-zA-Z0-9]+( [a-zA-Z0-9]+)*)

        Start
          ^Title +Price +Genre
          ^${title} +${price} +${genre} -> Record
    """.replace('_datetime_', dt_str)

    other_test_data = """
        Title                   Price       Genre
        =====================   ========    =============
        XML Developer's Guide   44.95       Computer
        Midnight Rain           5.95        Fantasy
        Maeve Ascendant         5.95        Fantasy
    """

    other_user_data = """
        comment__ Title column consists a list of mixed words
        comment__ Price column is number.  It can be digits or float number
        comment__ Genre column is a group of words
        Title                   Price       Genre
        keep__ =+ +=+ +=+
        mixed_words(var_title)   number(var_price)   words(var_genre) -> Record
    """

    other_template = """
        ################################################################################
        # Template is generated by templateapp Community Edition
        # Created by  : user1
        # Email       : user1@abcxyz.com
        # Company     : ABC XYZ LLC
        # Created date: _datetime_
        ################################################################################
        Value title (\\S*[a-zA-Z0-9]\\S*( \\S*[a-zA-Z0-9]\\S*)*)
        Value price ((\\d+)?[.]?\\d+)
        Value genre ([a-zA-Z0-9]+( [a-zA-Z0-9]+)*)

        Start
          # Title column consists a list of mixed words
          # Price column is number.  It can be digits or float number
          # Genre column is a group of words
          ^Title +Price +Genre
          ^=+ +=+ +=+
          ^${title} +${price} +${genre} -> Record
    """.replace('_datetime_', dt_str)

    test_info.test_data = dedent(test_data).strip()
    test_info.user_data = dedent(user_data).strip()
    test_info.template = dedent(template).strip()
    test_info.other_test_data = dedent(other_test_data).strip()
    test_info.other_user_data = dedent(other_user_data).strip()
    test_info.other_template = dedent(other_template).strip()
    test_info.expected_rows_count = 3
    test_info.expected_result = [
        dict(title="XML Developer's Guide", price="44.95", genre="Computer"),
        dict(title="Midnight Rain", price="5.95", genre="Fantasy"),
        dict(title="Maeve Ascendant", price="5.95", genre="Fantasy"),
    ]

    test_info.author = 'user1'
    test_info.email = 'user1@abcxyz.com'
    test_info.company = 'ABC XYZ LLC'

    base_dir = str(PurePath(Path(__file__).parent, 'data'))

    filename = str(PurePath(base_dir, 'unittest_script.txt'))
    with open(filename) as stream:
        script = stream.read()
        script = script.replace('_datetime_', dt_str)
        test_info.expected_unittest_script = script

    filename = str(PurePath(base_dir, 'pytest_script.txt'))
    with open(filename) as stream:
        script = stream.read()
        script = script.replace('_datetime_', dt_str)
        test_info.expected_pytest_script = script

    filename = str(PurePath(base_dir, 'snippet_script.txt'))
    with open(filename) as stream:
        script = stream.read()
        script = script.replace('_datetime_', dt_str)
        test_info.expected_snippet_script = script

    yield test_info


class TestParsedLine:

    @pytest.mark.parametrize(
        ('data', 'line', 'template_op', 'ignore_case'),
        [
            ('', '', '', False),
            ('abc xyz', 'abc xyz', '', False),
            ('ignore_case__ abc xyz', 'abc xyz', '', True),
            ('ignore_case__ abc xyz -> Record', 'abc xyz', 'Record', True)
        ]
    )
    def test_parsedline_attribute(self, data, line, template_op, ignore_case):
        obj = ParsedLine(data)
        assert obj.line == line
        assert obj.template_op == template_op
        assert obj.ignore_case == ignore_case

    @pytest.mark.parametrize(
        ('data', 'is_empty', 'is_a_word', 'is_not_containing_letter'),
        [
            ('', True, False, False),
            ('  ', True, False, False),
            ('abc xyz', False, False, False),
            ('abc', False, True, False),
            ('abc_xyz', False, True, False),
            ('abc.xyz', False, False, False),
            ('.*', False, False, True),
            ('==== ======= ===', False, False, True),
        ]
    )
    def test_parsedline_property(self, data, is_empty, is_a_word,
                                 is_not_containing_letter):
        obj = ParsedLine(data)
        assert obj.is_empty == is_empty
        assert obj.is_a_word == is_a_word
        assert obj.is_not_containing_letter == is_not_containing_letter

    @pytest.mark.parametrize(
        ('data', 'expected_result'),
        [
            (
                '',     # data
                ''      # expected_result
            ),
            (
                '  ',   # data
                ''      # expected_result
            ),
            (
                'Start',    # data
                'Start'     # expected_result
            ),
            (
                '===   ==========   ======',    # data
                '  ^=== +========== +======'    # expected_result
            ),
            (
                '===   ==========   ====== end()',  # data
                '  ^=== +========== +======$$'  # expected_result
            ),
            (
                'Today temperature is digits(var_degree) celsius.',     # data
                '  ^Today temperature is ${degree} celsius\\.'          # expected_result
            ),
            (
                'Today temperature is digits(var_degree) word(var_unit).',  # data
                '  ^Today temperature is ${degree} ${unit}\\.'              # expected_result
            ),
            (
                'Today temperature is digits(var_degree) word(var_unit). -> Record',    # data
                '  ^Today temperature is ${degree} ${unit}\\. -> Record'                # expected_result
            ),
            (
                'Today temperature is digits(var_degree, meta_data_Filldown) word(var_unit). -> Record',
                '  ^Today temperature is ${degree} ${unit}\\. -> Record'
            ),
        ]
    )
    def test_get_line_statement(self, data, expected_result):
        obj = ParsedLine(data)
        result = obj.get_statement()
        assert result == expected_result


class TestTemplateBuilder:
    def test_template(self, tc_info):
        factory = TemplateBuilder(
            user_data=tc_info.user_data,
            test_data=tc_info.test_data,
            author=tc_info.author,
            email=tc_info.email,
            company=tc_info.company,
        )
        assert factory.template == tc_info.template

    def test_template_with_flags(self, tc_info):
        factory = TemplateBuilder(
            user_data=tc_info.other_user_data,
            test_data=tc_info.other_test_data,
            author=tc_info.author,
            email=tc_info.email,
            company=tc_info.company,
        )
        assert factory.template == tc_info.other_template

    def test_verify(self, tc_info):
        factory = TemplateBuilder(
            user_data=tc_info.user_data,
            test_data=tc_info.test_data,
            author=tc_info.author,
            email=tc_info.email,
            company=tc_info.company,
        )
        is_verified = factory.verify()
        assert is_verified

    def test_verify_rows_count(self, tc_info):
        factory = TemplateBuilder(
            user_data=tc_info.user_data,
            test_data=tc_info.test_data,
            author=tc_info.author,
            email=tc_info.email,
            company=tc_info.company,
        )
        is_verified = factory.verify(
            expected_rows_count=tc_info.expected_rows_count
        )
        assert is_verified

    def test_verify_expected_result(self, tc_info):
        factory = TemplateBuilder(
            user_data=tc_info.user_data,
            test_data=tc_info.test_data,
            author=tc_info.author,
            email=tc_info.email,
            company=tc_info.company,
        )
        is_verified = factory.verify(
            expected_rows_count=tc_info.expected_rows_count,
            expected_result=tc_info.expected_result
        )
        assert is_verified

    def test_creating_unittest_script(self, tc_info):
        factory = TemplateBuilder(
            user_data=tc_info.user_data,
            test_data=tc_info.test_data,
            author=tc_info.author,
            email=tc_info.email,
            company=tc_info.company,
        )
        unittest_script = factory.create_unittest()
        assert unittest_script == tc_info.expected_unittest_script

    def test_creating_pytest_script(self, tc_info):
        factory = TemplateBuilder(
            user_data=tc_info.user_data,
            test_data=tc_info.test_data,
            author=tc_info.author,
            email=tc_info.email,
            company=tc_info.company,
        )
        pytest_script = factory.create_pytest()
        assert pytest_script == tc_info.expected_pytest_script

    def test_creating_snippet_script(self, tc_info):
        factory = TemplateBuilder(
            user_data=tc_info.user_data,
            test_data=tc_info.test_data,
            author=tc_info.author,
            email=tc_info.email,
            company=tc_info.company,
        )
        snippet_script = factory.create_python_test()
        assert snippet_script == tc_info.expected_snippet_script
