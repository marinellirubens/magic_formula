"""Module to contain the magic formula class to segregate the validation methods"""

import logging
from collections import namedtuple

import yahooquery

TICKER_INFO = namedtuple(
    'ticker_info',
    field_names=['financial_data', 'price', 'key_statistics',
                'balance_sheet', 'ebit', 'recommendation_trend']
)


class MagicFormula():
    def __init__(self, symbol: str, logger: logging.Logger) -> None:
        self.symbol = symbol
        self.logger = logger
        self.ticker_info = None

    def get_ticker_info(self) -> yahooquery.Ticker:
        """Returns the ticker info

        :param symbol: stock ticker
        :type symbol: str
        :return: Ticker info
        :rtype: yahooquery.Ticker
        """
        self.ticker: yahooquery.Ticker = yahooquery.Ticker(self.symbol)
        self.all_modules = self.ticker.all_modules[self.symbol]
        return self.ticker

    def get_ticker_data(self) -> bool:
        """Gets ticker data from the Ticker object

        :param symbol: Symbol from the ticker object
        :type symbol: str
        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns a named tuple with the information from the ticker
        :rtype: Tuple[bool, namedtuple]
        """
        if not self.valid_information_dict():
            return False
        
        self.financial_data = self.ticker.financial_data[self.symbol]
        self.ticker_price = self.all_modules.get('price', {})
        self.get_recomendation_trend()

        if not self.valid_industry():
            return False

        self.get_ebit()
        if not self.valid_ebit():
            return False

        self.key_statistics = self.all_modules['defaultKeyStatistics']
        self.balance_sheet = self.all_modules['balanceSheetHistory']
        
        self.fill_ticker_info()

        return True

    def fill_key_statistics(self) -> None:
        """Fill key statistics variable"""
        self.key_statistics = self.all_modules['defaultKeyStatistics']

    def fill_ticker_info(self) -> None:
        """Fills the variable ticker_info with a namedTuple from the type TICKER_INFO"""
        self.ticker_info = TICKER_INFO(
            self.financial_data, self.ticker_price,
            self.key_statistics, self.balance_sheet, self.ebit,
            self.recommendation_trend
        )

    def get_ebit(self) -> None:
        """Fill the variable ebit with information from the dict all_modules"""
        self.ebit = self.all_modules['incomeStatementHistory']['incomeStatementHistory'][0]['ebit']

    def get_recomendation_trend(self) -> tuple:
        """Returns a tuple with the information of the number of recomendations for buy and sell

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Tuple with the recomendation trend
        :rtype: tuple
        """
        try:
            strongBuy, buy, sell, strongSell = self.ticker.recommendation_trend[
                ['strongBuy', 'buy', 'sell', 'strongSell']
            ].sum()
            
            self.recommendation_trend = (strongBuy + buy), (sell + strongSell)
        except TypeError:
            self.recommendation_trend = (0, 0)

    def valid_ticker_info(self) -> bool:
        """Validates if the variable ticker_info has informations

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ticker_info is not None

    def valid_information_dict(self) -> bool:
        """Validates if the variable all_modules is an instance of dict

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return isinstance(self.all_modules, dict)

    def valid_industry(self) -> bool:
        """Validates if the industry of the company is valid for this method of calculation

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ticker.asset_profile[self.symbol]['industry'] not in ['Insurance—Diversified', 'Banks—Regional']

    def valid_ebit(self) -> bool:
        """Validates if the variable ebit is valid

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ebit > 0

    def valid_market_cap(self) -> bool:
        """Validates if the variable ticker_proce is valid

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ticker_price.get('marketCap', 0) > 0
