import os
import sys
import unittest
import logging


try:
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
    )
except:
    raise

from src.config import logging
from src.config import get_config
from src.config import set_logger


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
