from __future__ import absolute_import

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
    """Class to contains the main method for the magic formula

    :param symbol: Ticker symbol
    :type symbol: str
    :param logger: Logger object
    :type logger: logging.Logger
    :param ebit_min: Minimun ebit for the company, defaults to 1
    :type ebit_min: int, optional
    :param market_cap_min: Minimun market cap for the company, defaults to 0
    :type market_cap_min: int, optional
    """
    def __init__(self, symbol: str, logger: logging.Logger,
                 ebit_min: int = 1, market_cap_min: int = 0) -> None:
        self.symbol = symbol
        self.logger = logger
        self.ticker_info = None
        self._ebit_min = ebit_min
        self._market_cap_min = market_cap_min
        self.dividend_yield = 0
        self.ticker: yahooquery.Ticker = yahooquery.Ticker(self.symbol)
        self.asset_profile = self.ticker.asset_profile[self.symbol]
        self.all_modules = self.ticker.all_modules[self.symbol]

    def get_ticker_info(self) -> yahooquery.Ticker:
        """Returns the ticker info

        :return: Ticker info
        :rtype: yahooquery.Ticker
        """
        if isinstance(self.asset_profile, str):
            return None

        if not self.valid_information_dict():
            return None

        self.financial_data = self.ticker.financial_data[self.symbol]
        self.ticker_price = self.all_modules.get('price', {})

        self.logger.debug(self.symbol)
        self.industry = self.asset_profile['industry']
        self.fill_ebit()

        return self.ticker

    def fill_dividend_yield(self) -> None:
        """Fill dividend yield information"""
        self.dividend_yield = round(self.ticker.summary_detail[self.symbol].get('dividendYield', 0) * 100, 2)

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
        self.fill_dividend_yield()

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

    def fill_market_cap(self) -> None:
        """Fills variable market_cap"""
        self.market_cap = self.ticker_price.get('marketCap', 0)

    def fill_total_cash(self) -> None:
        """Fills variable total_cash"""
        self.total_cash = self.financial_data['totalCash']

    def fill_current_price(self) -> None:
        """Fills variable current_price"""
        self.current_price = self.financial_data['currentPrice']

    def fill_total_debt(self) -> None:
        """Fills variable total_debt"""
        self.total_debt = self.financial_data['totalDebt']

    def fill_long_name(self) -> None:
        """Fills variable long_name"""
        self.long_name = self.ticker_price.get('longName', '')

    def fill_short_name(self) -> None:
        """Fills variable short_name"""
        self.short_name = self.ticker_price.get('shortName', '')

    def fill_regular_market_time(self) -> None:
        """Fills variable regular_market_time"""
        self.regular_market_time = \
            self.ticker_price.get('regularMarketTime', 0)

    def fill_shares_outstanding(self) -> None:
        """Fills variable shares_outstanding"""
        self.shares_outstanding = \
            self.key_statistics.get(
                'sharesOutstanding',
                self.key_statistics.get('impliedSharesOutstanding', 0)
            )

    def fill_total_stockholder_equity(self) -> None:
        """Fills variable total_stockholder_equity"""
        self.total_stockholder_equity = \
            self.ticker_info.balance_sheet[
                'balanceSheetStatements'
            ][0]['totalStockholderEquity']

    def calculate_tev(self) -> float:
        """Calcullates the current tev (total enterprise value) and returns it

        :return: Total enterpris value
        :rtype: float
        """
        self.tev = self.total_stockholder_equity + self.total_debt
        return self.tev

    def calculate_earning_yield(self) -> float:
        """Calculates the current earning yield of the company

        :return: Current earning yeld
        :rtype: float
        """
        return round((self.tev / self.ebit), 2)
