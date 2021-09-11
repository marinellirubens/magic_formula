"""Module to contain the magic formula class to segregate
the validation methods"""

import logging
from collections import namedtuple

import yahooquery

TICKER_INFO = namedtuple(
    'ticker_info',
    field_names=['financial_data', 'price', 'key_statistics',
                 'balance_sheet', 'ebit', 'recommendation_trend']
)


class MagicFormula():
    def __init__(self, symbol: str, logger: logging.Logger,
                 ebit_min: int = 1, market_cap_min: int = 0) -> None:
        self.symbol = symbol
        self.logger = logger
        self.ticker_info = None
        self._ebit_min = ebit_min
        self._market_cap_min = market_cap_min

    def get_ticker_info(self) -> yahooquery.Ticker:
        """Returns the ticker info

        :return: Ticker info
        :rtype: yahooquery.Ticker
        """
        self.ticker: yahooquery.Ticker = yahooquery.Ticker(self.symbol)

        if isinstance(self.ticker.asset_profile[self.symbol], str):
            return None

        self.all_modules = self.ticker.all_modules[self.symbol]
        if not self.valid_information_dict():
            return None

        self.financial_data = self.ticker.financial_data[self.symbol]
        self.ticker_price = self.all_modules.get('price', {})
        self.industry = self.ticker.asset_profile[self.symbol]['industry']
        self.fill_ebit()

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

        self.get_recomendation_trend()

        if not self.valid_industry():
            return False

        if not self.valid_ebit():
            return False

        self.fill_key_statistics()
        self.fill_balance_sheet()
        self.fill_ticker_info()
        if not self.valid_ticker_info():
            return False

        self.fill_total_cash()
        self.fill_current_price()
        self.fill_total_debt()
        self.fill_market_cap()
        self.fill_long_name()
        self.fill_short_name()
        self.fill_regular_market_time()
        self.fill_shares_outstanding()
        self.fill_total_stockholder_equity()

        return True

    def fill_key_statistics(self) -> None:
        """Fill key statistics variable"""
        self.key_statistics = self.all_modules['defaultKeyStatistics']

    def fill_balance_sheet(self):
        """Fill key balance_sheet variable"""
        self.balance_sheet = self.all_modules['balanceSheetHistory']

    def fill_ticker_info(self) -> None:
        """Fills the variable ticker_info with a namedTuple
        from the type TICKER_INFO"""
        self.ticker_info = TICKER_INFO(
            self.financial_data, self.ticker_price,
            self.key_statistics, self.balance_sheet, self.ebit,
            self.recommendation_trend
        )

    def fill_ebit(self) -> None:
        """Fill the variable ebit with information from the dict all_modules"""
        self.ebit = \
            self.all_modules[
                'incomeStatementHistory']['incomeStatementHistory'][0]['ebit']

    def get_recomendation_trend(self) -> tuple:
        """Returns a tuple with the information of the number of
        recomendations for buy and sell

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Tuple with the recomendation trend
        :rtype: tuple
        """
        try:
            strongBuy, buy, sell, strongSell = \
                self.ticker.recommendation_trend[
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
        """Validates if the variable ticker_info has informations

        :return: Boolean with the result of the validation
        :rtype: boolvalid_information_dictan instance of dict

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return isinstance(self.all_modules, dict)

    def valid_industry(self) -> bool:
        """Validates if the industry of the company is valid
        for this method of calculation

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.industry not in ['Insurance—Diversified', 'Banks—Regional']

    def valid_ebit(self) -> bool:
        """Validates if the variable ebit is valid

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ebit >= self._ebit_min

    def valid_market_cap(self) -> bool:
        """Validates if the variable market_cap is valid

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.market_cap >= self._market_cap_min

    def fill_market_cap(self):
        """Fills variable market_cap"""
        self.market_cap = self.ticker_price.get('marketCap', 0)

    def fill_total_cash(self):
        self.total_cash = self.financial_data['totalCash']

    def fill_current_price(self):
        self.current_price = self.financial_data['currentPrice']

    def fill_total_debt(self):
        self.total_debt = self.financial_data['totalDebt']

    def fill_long_name(self):
        self.long_name = self.ticker_price.get('longName', '')

    def fill_short_name(self):
        self.short_name = self.ticker_price.get('shortName', '')

    def fill_regular_market_time(self):
        self.regular_market_time = \
            self.ticker_price.get('regularMarketTime', 0)

    def fill_shares_outstanding(self):
        self.shares_outstanding = \
            self.key_statistics.get(
                'sharesOutstanding',
                self.key_statistics.get('impliedSharesOutstanding', 0)
            )

    def fill_total_stockholder_equity(self):
        self.total_stockholder_equity = \
            self.ticker_info.balance_sheet[
                'balanceSheetStatements'
            ][0]['totalStockholderEquity']

    def calculate_tev(self):
        self.tev = self.total_stockholder_equity + self.total_debt
        return self.tev

    def calculate_earning_yield(self):
        return round((self.tev / self.ebit), 2)
