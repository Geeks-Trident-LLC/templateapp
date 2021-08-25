import pytest

from templateapp.core import ParsedLine


class TestParsedLine:

    @pytest.mark.parametrize(
        ('data', 'line', 'template_op', 'ignore_case'),
        [
            ('', '', '', False),
            ('abc xyz', 'abc xyz', '', False),
            ('ignore_case abc xyz', 'abc xyz', '', True),
            ('ignore_case abc xyz -> Record', 'abc xyz', 'Record', True)
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
                '  ^=== +========== +======\\s*$$'  # expected_result
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
                'Today temperature is digits(var_degree, Filldown) word(var_unit). -> Record',
                '  ^Today temperature is ${degree} ${unit}\\. -> Record'
            ),
        ]
    )
    def test_get_line_statement(self, data, expected_result):
        obj = ParsedLine(data)
        result = obj.get_statement()
        assert result == expected_result
