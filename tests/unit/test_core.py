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
        ('data', 'is_empty'),
        [
            ('', True),
            ('  ', True),
            ('abc xyz', False),
        ]
    )
    def test_parsedline_property(self, data, is_empty):
        obj = ParsedLine(data)
        assert obj.is_empty == is_empty
