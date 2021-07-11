"""Module to contain the magic formula class to segregate the validation methods"""

import yahooquery
from collections import namedtuple
from typing import Tuple
import logging


class MagicFormula():
    def __init__(self) -> None:
        pass


    def get_ticker_info(self, symbol: str, logger: logging.Logger) -> yahooquery.Ticker:
        """Returns the ticker info

        :param symbol: stock ticker
        :type symbol: str
        :param logger: Logger object
        :type logger: logging.Logger
        :return: Ticker info
        :rtype: yahooquery.Ticker
        """
        self.ticker = yahooquery.Ticker(symbol)
        return self.ticker


    def get_ticker_data(self, symbol: str, ticker: yahooquery.Ticker) -> Tuple[bool, namedtuple]:
        """Gets ticker data from the Ticker object

        :param symbol: Symbol from the ticker object
        :type symbol: str
        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns a named tuple with the information from the ticker
        :rtype: Tuple[bool, namedtuple]
        """
        ticker_info = namedtuple(
            'ticker_info',
            field_names=['financial_data', 'price', 'key_statistics',
                        'balance_sheet', 'ebit', 'recommendation_trend']
        )

        all_modules = ticker.all_modules[symbol]
        financial_data = ticker.financial_data[symbol]
        ticker_price = all_modules.get('price', {})
        recommendation_trend = self.get_recomendation_trend(ticker=ticker)

        ebit = all_modules['incomeStatementHistory']['incomeStatementHistory'][0]['ebit']
        key_statistics = all_modules['defaultKeyStatistics']
        balance_sheet = all_modules['balanceSheetHistory']

        ticker_tuple = ticker_info(financial_data, ticker_price,
                                key_statistics, balance_sheet, ebit,
                                recommendation_trend)
        return ticker_tuple


    def get_recomendation_trend(self, ticker: yahooquery.Ticker) -> tuple:
        """Returns a tuple with the information of the number of recomendations for buy and sell

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Tuple with the recomendation trend
        :rtype: tuple
        """
        try:
            strongBuy, buy, sell, strongSell = ticker.recommendation_trend[
                ['strongBuy', 'buy', 'sell', 'strongSell']
            ].sum()
            
            recommendation_trend = (strongBuy + buy), (sell + strongSell)
        except TypeError:
            recommendation_trend = (0, 0)

        return recommendation_trend


    def ticker_is_valid(self, symbol: str, logger: logging.Logger) -> Tuple[bool, namedtuple]:
        """Verify if the ticker is valid for the formula

        :param symbol: Ticker symbol
        :type symbol: str
        :param logger: Logger object
        :type logger: logging.Logger
        :return: Tuple with the boolean defining if is valid, and the informations for the stock
        :rtype: Tuple[bool, namedtuple]
        """
        # TODO: change this function into small functions
        logger.debug(f'Validating ticker: {symbol}')
        
        ticker_info = namedtuple(
            'ticker_info',
            field_names=['financial_data', 'price', 'key_statistics',
                        'balance_sheet', 'ebit', 'recommendation_trend']
        )
        
        ticker = self.get_ticker_info(symbol, logger)
        all_modules = ticker.all_modules[symbol]
        if not isinstance(all_modules, dict):
            return False, tuple()

        financial_data = ticker.financial_data[symbol]
        ticker_price = all_modules.get('price', {})
            
        recommendation_trend = self.get_recomendation_trend(ticker=ticker)

        if ticker.asset_profile[symbol]['industry'] in ['Insurance—Diversified', 'Banks—Regional']:
            return False, tuple()

        ebit = all_modules['incomeStatementHistory']['incomeStatementHistory'][0]['ebit']
        if ebit <= 0:
            return False, tuple()

        market_cap = ticker_price.get('marketCap', 0)
        if market_cap <= 0:
            return False, tuple()

        key_statistics = all_modules['defaultKeyStatistics']
        balance_sheet = all_modules['balanceSheetHistory']

        logger.debug(f'Ticker: {symbol} validated and its Valid.')
        
        return True, ticker_info(financial_data, ticker_price,
                                key_statistics, balance_sheet, ebit,
                                recommendation_trend)

