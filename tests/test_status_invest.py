"""Module to test methods from module status_invest"""
import os
import sys
import unittest
from unittest import mock

import requests


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests')))


from src.setup import get_config, set_logger
from src.status_invest import get_ibrx_info, get_ticker_roic_info

from config_tests import STATUS_INVEST_URL_RETURN


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code, file_content):
            self.status_code = status_code
            self.content = file_content

    if 'advancedsearchresult' in args[0]:
        return MockResponse(200, STATUS_INVEST_URL_RETURN)

    if 'statusinvest' in args[0]:
        with open('tests/example_brx100.txt', 'rb') as file:
            file_content = file.read()
        return MockResponse(200, file_content)

    return MockResponse(404, None)


class TestStocksGreenblatMagicFormula(unittest.TestCase):
    def test_get_ibrx_info(self):
        config = get_config('tests/teste.json')
        test_logger = set_logger()
        with mock.patch('requests.get', side_effect=mocked_requests_get):
            ticker_info = get_ibrx_info(config['BRX10_URL'], logger=test_logger)
            self.assertEqual({'B3SA3', 'PETR3'}, ticker_info)
        
    def test_get_ticker_roic_info(self):
        config = get_config('tests/teste.json')
        test_logger = set_logger()

        with mock.patch('requests.get', side_effect=mocked_requests_get):
            # teste = requests.get(config['STATUS_INVEST_URL']).content
            # assert 'a' == teste
            roic_info = get_ticker_roic_info(config['STATUS_INVEST_URL'])
            self.assertEqual({'CPLE6': {'roic_index': 0, 'roic': 10.77}, 'CAMB3': {'roic_index': 1, 'roic': 1.58}}, roic_info)
