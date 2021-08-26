"""Module containing the exception class for templateapp."""


class TemplateError(Exception):
    """Use to capture error template construction."""


class TemplateParsedLineError(TemplateError):
    """Use to capture error parsed line for template builder."""


class TemplateBuilderError(Exception):
    """Use to capture error template construction."""
