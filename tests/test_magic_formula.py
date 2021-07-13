"""Module to test methods from module magic_formula"""
import os
import sys
import unittest
import logging
import yahooquery

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests')))


from src.magic_formula import MagicFormula
from src.setup import set_logger


class TestMagicFormula(unittest.TestCase):
    def setUp(self):
        self.logger = logging.Logger(__name__)
        self.logger = set_logger(self.logger)
        
    def test_magic_formula_instance(self):
        itsa = MagicFormula('ITSA4.SA', self.logger)

        self.assertIsInstance(itsa, MagicFormula)
        self.assertEqual(itsa.symbol, 'ITSA4.SA')
        self.assertIs(itsa.logger, self.logger)
        self.assertIsNone(itsa.ticker_info)

    def test_validate_ticker_info(self):
        itsa = MagicFormula('ITSA4.SA', self.logger)
        itsa.get_ticker_info()
        self.assertIsNotNone(itsa.ticker)
        self.assertIsInstance(itsa.ticker, yahooquery.Ticker)

    def test_valid_recomendation_trend(self):
        itsa = MagicFormula('ITSA4.SA', self.logger)
        itsa.get_ticker_info()
        itsa.get_recomendation_trend()
        # TODO: Imcluir testes de quando esta valido
        self.assertIsInstance(itsa.recommendation_trend, tuple)

    def test_valid_ticker_info(self):
        itsa = MagicFormula('ITSA4.SA', self.logger)
        itsa.get_ticker_info()

        self.assertFalse(itsa.valid_ticker_info())
