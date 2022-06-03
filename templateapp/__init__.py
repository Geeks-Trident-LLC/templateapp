"""Top-level module for templateapp.

- allow end-user to create template or test script on GUI application.
"""

from templateapp.core import ParsedLine
from templateapp.core import TemplateBuilder
from templateapp.config import version
from templateapp.config import edition

__version__ = version
__edition__ = edition

__all__ = [
    'ParsedLine',
    'TemplateBuilder',
    'version',
    'edition',
]
