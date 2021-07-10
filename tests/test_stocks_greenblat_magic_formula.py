from __future__ import absolute_import

import os
import sys
import unittest
import logging
from unittest import mock
import yahooquery

try:
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
    )
except:
    raise

from src import stocks_greenblat_magic_formula as green
from src.stocks_greenblat_magic_formula import logging


def scenario_logger():
    logger = logging.getLogger(__name__)
    return logger


class TestStocksGreenblatMagicFormula(unittest.TestCase):
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

    def test_get_ticker_data(self):
        pass

    def test_get_recomendation_trend(self):
        logger = scenario_logger()
        logger: logging.Logger = green.set_logger(logger)

        ticker = green.get_ticker_info('ITSA4.SA', logger)
        recomendation_trend = green.get_recomendation_trend(ticker=ticker)

        self.assertIsNotNone(recomendation_trend)
        self.assertIsInstance(recomendation_trend, tuple)
