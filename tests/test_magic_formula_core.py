"""Module to test methods from module magic_formula"""
import os
import sys
import unittest
import logging
import yahooquery
from unittest import mock


sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests')))


from magic_formula.magic_formula_core import MagicFormula, TICKER_INFO
from magic_formula.config import set_logger


def mock_fill_ticker_info(self):
    self.ticker_info = None


class TestMagicFormula(unittest.TestCase):
    def setUp(self):
        self.logger = logging.Logger(__name__)
        self.logger = set_logger(self.logger)
        self.wege = MagicFormula('WEGE3.SA', self.logger)
        self.wege.get_ticker_info()

    def test_magic_formula_instance(self):
        self.assertIsInstance(self.wege, MagicFormula)
        self.assertEqual(self.wege.symbol, 'WEGE3.SA')
        self.assertIs(self.wege.logger, self.logger)
        self.assertIsNone(self.wege.ticker_info)

    def test_validate_ticker_info(self):
        self.assertIsNotNone(self.wege.ticker)
        self.assertIsInstance(self.wege.ticker, yahooquery.Ticker)

    def test_valid_recomendation_trend(self):
        self.wege.get_recomendation_trend()
        self.assertIsInstance(self.wege.recommendation_trend, tuple)

    def test_valid_recomendation_trend_error(self):
        self.wege.get_recomendation_trend()

        self.assertIsNotNone(self.wege.recommendation_trend)
        self.assertIsInstance(self.wege.recommendation_trend, tuple)
        self.assertIsInstance(self.wege.recommendation_trend[0], int)
        self.assertIsInstance(self.wege.recommendation_trend[1], int)

    def test_fill_key_statistics(self):
        self.wege.fill_key_statistics()

        self.assertIsNotNone(self.wege.key_statistics)
        self.assertIsInstance(self.wege.key_statistics, dict)
        self.assertNotEqual(self.wege.key_statistics, {})

    def test_valid_ticker_info(self):
        self.assertFalse(self.wege.valid_ticker_info())

    def test_get_ebit(self):
        self.wege.fill_ebit()

        self.assertIsNotNone(self.wege.ebit)
        self.assertIsInstance(self.wege.ebit, int)
        self.assertGreater(self.wege.ebit, 0)

    def test_fill_balance_sheet(self):
        self.wege.fill_balance_sheet()

        self.assertIsNotNone(self.wege.balance_sheet)
        self.assertIsInstance(self.wege.balance_sheet, dict)
        self.assertIsNot(self.wege.balance_sheet, {})

    def test_valid_market_cap(self):
        self.wege.fill_market_cap()
        return_ = self.wege.valid_market_cap()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)

    def test_valid_ebit(self):
        self.wege.fill_ebit()
        return_ = self.wege.valid_ebit()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)

        self.wege.ebit = -1
        return_ = self.wege.valid_ebit()
        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_valid_industry(self):
        return_ = self.wege.valid_industry()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)
        self.wege.industry = 'Banks—Regional'

        return_ = self.wege.valid_industry()

        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_valid_information_dict(self):
        return_ = self.wege.valid_information_dict()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)

        self.wege.all_modules = 'a'
        return_ = self.wege.valid_information_dict()

        self.assertFalse(return_)

        self.wege.all_modules = 'a'
        return_ = self.wege.get_ticker_info()
        self.assertIsNone(return_)

    def test_fill_ticker_info(self):
        self.wege.get_ticker_data()

        self.assertIsNotNone(self.wege.ticker_info)
        self.assertIsInstance(self.wege.ticker_info, TICKER_INFO)

    def test_get_ticker_data_false_valid_dict(self):
        self.wege.all_modules = 'a'
        return_ = self.wege.get_ticker_data()

        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_get_ticker_data_false_valid_industry(self):
        self.wege.industry = 'Banks—Regional'
        return_ = self.wege.get_ticker_data()

        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_get_ticker_data_false_valid_ebit(self):
        self.wege.ebit = -1
        return_ = self.wege.get_ticker_data()

        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_get_ticker_info_valid_information_dict_false(self):
        return_ = self.wege.get_ticker_info()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)

        self.wege.asset_profile = 'teste'
        return_ = self.wege.get_ticker_info()

        self.assertIsNone(return_)
        self.assertFalse(return_)

    def test_fill_total_stockholder_equity(self):
        _ = self.wege.get_ticker_data()
        self.wege.fill_total_stockholder_equity()

        self.assertIsNotNone(self.wege.total_stockholder_equity)
        self.assertGreater(self.wege.total_stockholder_equity, 0)

    def test_calculate_tev(self):
        _ = self.wege.get_ticker_data()
        self.wege.fill_total_stockholder_equity()
        self.wege.calculate_tev()

        self.assertIsNotNone(self.wege.tev)
        self.assertGreater(self.wege.tev, 0)

    def test_calculate_earning_yield(self):
        _ = self.wege.get_ticker_data()
        self.wege.fill_total_stockholder_equity()
        self.wege.calculate_tev()
        ey = self.wege.calculate_earning_yield()

        self.assertIsNotNone(ey)
        self.assertGreater(ey, 0)
        self.assertEqual(ey, (round((self.wege.tev / self.wege.ebit), 2)))

    def test_valid_ticker_info(self):
        with mock.patch('src.magic_formula.MagicFormula.fill_ticker_info', mock_fill_ticker_info):
            _ = self.wege.get_ticker_data()

            self.assertFalse(self.wege.valid_ticker_info())
            self.assertIsNone(self.wege.ticker_info)
