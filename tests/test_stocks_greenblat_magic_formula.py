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


def scenario_logger():
    logger = logging.getLogger(__name__)
    return logger


class TestStocksGreenblatMagicFormula(unittest.TestCase):
    def test_get_config(self):
        config = green.get_config('tests/teste.json')
        self.assertIsNotNone(config)
        self.assertIsInstance(config, dict)
        self.assertEqual(config['BRX10_URL'], 'https://statusinvest.com.br/indices/indice-brasil-100')
        
    def test_set_logger(self):
        logger = scenario_logger()
        logger_formated: logging.Logger = green.set_logger(logger)
        
        self.assertEqual(logger_formated.level, 10)
        self.assertIsInstance(logger_formated.handlers[0], logging.handlers.RotatingFileHandler)
        self.assertIsInstance(logger_formated.handlers[1], logging.StreamHandler)

        format = '%(asctime)s - %(name)s - (%(threadName)-10s) - %(levelname)s - %(message)s'
        for handler in logger_formated.handlers:
            self.assertEqual(handler.formatter._fmt, format)

    def test_get_ticker_info_assert_is_dict(self):
        logger = scenario_logger()
        logger: logging.Logger = green.set_logger(logger)
        
        stock = green.get_ticker_info('ITSA4.SA', logger)
        self.assertIsInstance(stock, yahooquery.Ticker)

    def test_get_ticker_info_assert_is_none(self):
        logger = scenario_logger()
        logger: logging.Logger = green.set_logger(logger)
        
        stock = green.get_ticker_info('ITSA4.SA', logger)
        self.assertIsNotNone(stock)

