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
