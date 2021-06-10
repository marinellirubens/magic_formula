from __future__ import absolute_import

import os
import sys
import unittest
import logging
from unittest import mock
import yahooquery

try:
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    )
except:
    raise

from src import stocks_greenblat_magic_formula as green
from src.stocks_greenblat_magic_formula import logging

class TestStocksGreenblatMagicFormula(unittest.TestCase):
    def test_get_config(self):
        config = green.get_config('tests/teste.json')
        self.assertIsNotNone(config)
        self.assertIsInstance(config, dict)
        self.assertEqual(config['BRX10_URL'], 'https://statusinvest.com.br/indices/indice-brasil-100')
        
    def test_set_logger(self):
        logger = logging.getLogger(__name__)
        logger_formated: logging.Logger = green.set_logger(logger)
        
        self.assertEqual(logger_formated.level, 10)
        self.assertIsInstance(logger_formated.handlers[0], logging.handlers.RotatingFileHandler)
        self.assertIsInstance(logger_formated.handlers[1], logging.StreamHandler)

        format = '%(asctime)s - %(name)s - (%(threadName)-10s) - %(levelname)s - %(message)s'
        for handler in logger_formated.handlers:
            self.assertEqual(handler.formatter._fmt, format)
