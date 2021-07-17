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


from src.magic_formula import MagicFormula, TICKER_INFO
from src.config import set_logger


def mock_fill_ticker_info(self):
    self.ticker_info = None


class TestMagicFormula(unittest.TestCase):
    def setUp(self):
        self.logger = logging.Logger(__name__)
        self.logger = set_logger(self.logger)

    def test_magic_formula_instance(self):
        wege = MagicFormula('WEGE3.SA', self.logger)

        self.assertIsInstance(wege, MagicFormula)
        self.assertEqual(wege.symbol, 'WEGE3.SA')
        self.assertIs(wege.logger, self.logger)
        self.assertIsNone(wege.ticker_info)

    def test_validate_ticker_info(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()
        self.assertIsNotNone(wege.ticker)
        self.assertIsInstance(wege.ticker, yahooquery.Ticker)

    def test_valid_recomendation_trend(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()
        wege.get_recomendation_trend()
        # TODO: Imcluir testes de quando esta valido
        self.assertIsInstance(wege.recommendation_trend, tuple)

    def test_valid_recomendation_trend_error(self):
        wege = MagicFormula('NEOE3.SA', self.logger)
        wege.get_ticker_info()

        wege.get_recomendation_trend()

        self.assertIsInstance(wege.recommendation_trend, tuple)
        self.assertEqual(wege.recommendation_trend, (0, 0))

    def test_fill_key_statistics(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()

        wege.fill_key_statistics()

        self.assertIsNotNone(wege.key_statistics)
        self.assertIsInstance(wege.key_statistics, dict)
        self.assertNotEqual(wege.key_statistics, {})

    def test_valid_ticker_info(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()

        self.assertFalse(wege.valid_ticker_info())

    def test_get_ebit(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()
        wege.fill_ebit()

        self.assertIsNotNone(wege.ebit)
        self.assertIsInstance(wege.ebit, int)
        self.assertGreater(wege.ebit, 0)

    def test_fill_balance_sheet(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()
        wege.fill_balance_sheet()

        self.assertIsNotNone(wege.balance_sheet)
        self.assertIsInstance(wege.balance_sheet, dict)
        self.assertIsNot(wege.balance_sheet, {})

    def test_valid_market_cap(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()
        wege.fill_market_cap()
        return_ = wege.valid_market_cap()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)

    def test_valid_ebit(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()
        wege.fill_ebit()
        return_ = wege.valid_ebit()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)

        wege.ebit = -1
        return_ = wege.valid_ebit()
        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_valid_industry(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()
        return_ = wege.valid_industry()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)
        wege.industry = 'Banks—Regional'

        return_ = wege.valid_industry()

        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_valid_information_dict(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()
        return_ = wege.valid_information_dict()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)

        wege.all_modules = 'a'
        return_ = wege.valid_information_dict()

        self.assertFalse(return_)

    def test_fill_ticker_info(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()
        wege.get_ticker_data()

        self.assertIsNotNone(wege.ticker_info)
        self.assertIsInstance(wege.ticker_info, TICKER_INFO)

    def test_get_ticker_data_false_valid_dict(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()

        wege.all_modules = 'a'
        return_ = wege.get_ticker_data()

        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_get_ticker_data_false_valid_industry(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()

        wege.industry = 'Banks—Regional'
        return_ = wege.get_ticker_data()

        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_get_ticker_data_false_valid_ebit(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()

        wege.ebit = -1
        return_ = wege.get_ticker_data()

        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_get_ticker_info_valid_information_dict_false(self):
        wege = MagicFormula('DTEXa3.SA', self.logger)
        return_ = wege.get_ticker_info()

        self.assertIsNone(return_)
        self.assertFalse(return_)

    def test_fill_total_stockholder_equity(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()

        return_ = wege.get_ticker_data()
        wege.fill_total_stockholder_equity()

        self.assertIsNotNone(wege.total_stockholder_equity)
        self.assertGreater(wege.total_stockholder_equity, 0)

    def test_calculate_tev(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()

        return_ = wege.get_ticker_data()
        wege.fill_total_stockholder_equity()
        wege.calculate_tev()

        self.assertIsNotNone(wege.tev)
        self.assertGreater(wege.tev, 0)

    def test_calculate_earning_yield(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()

        return_ = wege.get_ticker_data()
        wege.fill_total_stockholder_equity()
        wege.calculate_tev()
        ey = wege.calculate_earning_yield()

        self.assertIsNotNone(ey)
        self.assertGreater(ey, 0)
        self.assertEqual(ey, (round((wege.tev / wege.ebit), 2)))

    def test_valid_ticker_info(self):
        wege = MagicFormula('WEGE3.SA', self.logger)
        wege.get_ticker_info()

        with mock.patch('src.magic_formula.MagicFormula.fill_ticker_info', mock_fill_ticker_info) as filler:
            return_ = wege.get_ticker_data()

            self.assertFalse(wege.valid_ticker_info())
            self.assertIsNone(wege.ticker_info)