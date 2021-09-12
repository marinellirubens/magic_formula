from __future__ import absolute_import

import os
import sys
import unittest
import logging
from unittest import mock


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from magic_formula import magic_formula_main as green


def scenario_logger():
    logger = logging.getLogger(__name__)
    return logger


class TestMainModule(unittest.TestCase):
    @mock.patch('builtins.exit')
    @mock.patch('builtins.print')
    def test_print_version(self, mock_print, mock_exit):
        green.show_version()

        mock_print.assert_called_with(f'MagicFormula v{green.__VERSION__}')
        mock_exit.assert_called_with(0)
