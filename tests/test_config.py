import os
import sys
import unittest
import logging


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from src.config import get_config
from src.config import set_logger
from src.config import get_arguments


def scenario_logger():
    logger = logging.getLogger(__name__)
    return logger


class TestSetup(unittest.TestCase):
    def test_get_config(self):
        config = get_config('tests/teste.json')
        self.assertIsNotNone(config)
        self.assertIsInstance(config, dict)
        self.assertEqual(config['BRX10_URL'], 'https://statusinvest.com.br/indices/indice-brasil-100')

    def test_set_logger(self):
        logger = scenario_logger()
        logger_formated: logging.Logger = set_logger(logger)

        self.assertEqual(logger_formated.level, 10)
        self.assertIsInstance(logger_formated.handlers[0], logging.handlers.RotatingFileHandler)
        self.assertIsInstance(logger_formated.handlers[1], logging.StreamHandler)

        format = '%(asctime)s - %(name)s - (%(threadName)-10s) - %(levelname)s - %(message)s'
        for handler in logger_formated.handlers:
            self.assertEqual(handler.formatter._fmt, format)

    def test_get_arguments_defaults(self):
        options = get_arguments([])
        self.assertFalse(options.version)
        self.assertEqual(options.index, ['BRX100'])
        self.assertEqual(options.ebit, 1)
        self.assertEqual(options.market_cap, 0)
        self.assertEqual(options.qty, 15)

    def test_get_arguments_arguments(self):
        arguments = [
            [['-V'], [True, ['BRX100'], 1, 0, 15]],
            [['-e', '2'], [False, ['BRX100'], 2, 0, 15]],
            [['-i', 'IBOV', '-m', '50000'], [False, ['IBOV'], 1, 50000, 15]],
            [['-i', 'SMALL', '-m', '50001', '-q', '100'], [False, ['SMALL'], 1, 50001, 100]],
        ]
        for args in arguments:
            options = get_arguments(args[0])
            self.assertEqual(options.version, args[1][0])
            self.assertEqual(options.index, args[1][1])
            self.assertEqual(options.ebit, args[1][2])
            self.assertEqual(options.market_cap, args[1][3])
            self.assertEqual(options.qty, args[1][4])
