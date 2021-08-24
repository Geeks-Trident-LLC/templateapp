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
        ('data', 'is_empty', 'has_template_op', 'is_ignore_case'),
        [
            ('', True, False, False),
            ('abc xyz', False, False, False),
            ('ignore_case abc xyz', False, False, True),
            ('ignore_case abc xyz -> Record', False, True, True)
        ]
    )
    def test_parsedline_property(self, data, is_empty,
                                 has_template_op, is_ignore_case):
        obj = ParsedLine(data)
        assert obj.is_empty == is_empty
        assert obj.has_template_op == has_template_op
        assert obj.is_ignore_case == is_ignore_case
