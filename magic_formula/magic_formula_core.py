"""Module to contain the magic formula class to segregate the validation methods"""
from __future__ import absolute_import

import logging
from dataclasses import dataclass
from typing import Union
import yahooquery


@dataclass
class RecomenationTrend:
    """Recommendation trend variables"""
    buy_counter: int
    sell_counter: int


@dataclass
class TickerInfo:
    """Ticker info variables"""
    financial_data: dict
    ticker_price: dict
    key_statistics: dict
    balance_sheet: dict
    ebit: float
    recommendation_trend: RecomenationTrend
    asset_profile: Union[dict, str]
    industry: list
    summary_detail: dict
    market_cap: float
    total_cash: float
    dividend_yield: float
    current_price: float
    long_name: str
    short_name: str
    regular_market_time: str
    shares_outstanding: float
    total_stockholder_equity: float
    total_debt: float
    all_modules_found: bool = False


class TickerInfoBuilder:
    """Class to build the TickerInfo object"""
    def __init__(self, ticker: yahooquery.Ticker, symbol: str) -> None:
        self.ticker= ticker
        self.symbol = symbol

    def build(self) -> TickerInfo:
        """Builds the TickerInfo object

        :return: Returns the TickerInfo object
        :rtype: TickerInfo
        """
        ticker_info = TickerInfo(
            all_modules_found=self.valid_all_modules(),
            asset_profile=self.get_asset_profile(),
            financial_data=self.get_financial_data(),
            ticker_price=self.get_ticker_price(),
            industry=self.get_industry(),
            summary_detail=self.get_summary_detail(),
            balance_sheet=self.get_balance_sheet(),
            ebit=self.get_ebit(),
            key_statistics=self.get_key_statistics(),
            recommendation_trend=self.get_recomendation_trend(),
            market_cap=self.get_market_cap(),
            total_cash=self.get_total_cash(),
            dividend_yield=self.get_dividend_yield(),
            current_price=self.get_current_price(),
            long_name=self.get_long_name(),
            short_name=self.get_short_name(),
            regular_market_time=self.get_regular_market_time(),
            shares_outstanding=self.get_shares_outstanding(),
            total_stockholder_equity=self.get_total_stockholder_equity(),
            total_debt=self.get_total_debt()
        )
        return ticker_info

    def set_ticker(self, ticker: yahooquery.Ticker):
        """Set Builder ticker

        :tick: Ticker object
        :type tick: yahooquery.Ticker
        """
        self.ticker = ticker

    def set_symbol(self, symbol: str):
        """Set Builder symbol

        :param symbol: Symbol
        :type symbol: str
        """
        self.symbol = symbol

    def valid_all_modules(self) -> bool:
        """Validates if all_modules is a dict

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns True if all_modules is a dict
        :rtype: bool
        """
        return self.get_all_modules() != {}

    def get_all_modules(self) -> dict:
        """returns all modules variable

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the all modules
        :rtype: dict
        """
        all_modules = self.ticker.all_modules.get(self.symbol, {})
        if isinstance(all_modules, str):
            return {}

        return all_modules

    def get_industry(self) -> list:
        """Fill the variable industry with information from the dict all_modules

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the industry
        :rtype: list
        """
        asset_profile = self.get_asset_profile()
        return asset_profile.get('industry')

    def get_asset_profile(self) -> dict:
        """Fills variable asset_profile

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the asset profile
        :rtype: dict
        """
        return self.ticker.asset_profile.get(self.symbol, {})

    def get_ticker_price(self) -> dict:
        """Fills variable ticker_price

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the ticker price
        :rtype: dict
        """
        return self.get_all_modules().get('price', {})

    def get_financial_data(self) -> dict:
        """Fills variable financial_data

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the financial data
        :rtype: dict
        """
        return self.ticker.financial_data.get(self.symbol, {})

    def get_dividend_yield(self) -> float:
        """Fill dividend yield information

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the dividend yield
        :rtype: float
        """
        return round(self.ticker.summary_detail.get(self.symbol, {}).get('dividendYield', 0)
                     * 100, 2)

    def get_key_statistics(self) -> dict:
        """Fill key statistics variable

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the key statistics
        :rtype: dict
        """
        return self.get_all_modules().get('defaultKeyStatistics', {})

    def get_balance_sheet(self) -> dict:
        """Fill key balance_sheet variable

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the balance sheet
        :rtype: dict
        """
        balance_sheet = self.get_all_modules().get('balanceSheetHistory', {})
        return balance_sheet

    def get_summary_detail(self) -> dict:
        """Fills variable summary_detail

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the summary detail
        :rtype: dict
        """
        return self.ticker.summary_detail.get(self.symbol)

    def get_recomendation_trend(self) -> RecomenationTrend:
        """Returns a RecomenationTrend with the information of the number of
        recomendations for buy and sell

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the RecomenationTrend object
        :rtype: RecomenationTrend
        """
        try:
            strong_buy, buy, sell, strong_sell = \
                self.ticker.recommendation_trend[
                    ['strongBuy', 'buy', 'sell', 'strongSell']
                ].sum()

            return RecomenationTrend((strong_buy + buy), (sell + strong_sell))
        except TypeError:
            return RecomenationTrend(0, 0)

    def get_ebit(self) -> float:
        """Fill the variable ebit with information from the dict all_modules

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the ebit
        :rtype: float
        """
        income_statement_history = self.get_all_modules().\
            get('incomeStatementHistory', {})
        income_statement_history_quarterly = income_statement_history.get(
            'incomeStatementHistoryQuarterly', {})

        if income_statement_history_quarterly == {}:
            income_statement_history_quarterly = income_statement_history.get(
                'incomeStatementHistory', {})

        if income_statement_history_quarterly == {}:
            return 0

        ebit = income_statement_history_quarterly[0].get('ebit', 0)

        return ebit

    def get_market_cap(self) -> float:
        """Fills variable market_cap

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the market cap
        :rtype: float
        """
        market_cap = self.ticker.all_modules.get(self.symbol).get('price', {}).get('marketCap', 0)
        return market_cap

    def get_total_cash(self) -> float:
        """Fills variable total_cash

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the total cash
        :rtype: float
        """
        total_cash = self.ticker.financial_data.get(self.symbol, {}).get('totalCash')
        return total_cash

    def get_current_price(self) -> float:
        """Fills variable current_price

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the current price
        :rtype: float
        """
        return self.ticker.financial_data.get(self.symbol, {}).get('currentPrice')

    def get_total_debt(self) -> float:
        """Fills variable total_debt

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the total debt
        :rtype: float
        """
        return self.get_financial_data().get('totalDebt')

    def get_long_name(self) -> str:
        """Fills variable long_name

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the long name
        :rtype: str"""
        return self.get_ticker_price().get('longName', '')

    def get_short_name(self) -> str:
        """Fills variable short_name

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the short name
        :rtype: str
        """
        return self.get_ticker_price().get('shortName', '')

    def get_regular_market_time(self) -> str:
        """Fills variable regular_market_time

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the regular market time
        :rtype: str
        """
        return self.get_ticker_price().get('regularMarketTime', 0)

    def get_shares_outstanding(self) -> str:
        """Fills variable shares_outstanding

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the shares outstanding
        :rtype: str
        """
        return \
            self.get_key_statistics().get(
                'sharesOutstanding',
                self.get_key_statistics().get('impliedSharesOutstanding', 0)
            )

    def get_total_stockholder_equity(self) -> int:
        """Fills variable total_stockholder_equity

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        :return: Returns the total stockholder equity
        :rtype: int
        """
        return self.get_balance_sheet().get('balanceSheetStatements', {})[0]\
            .get('totalStockholderEquity', 0)


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
        self.ticker_info: TickerInfo = None
        self.ebit_min = ebit_min
        self.market_cap_min = market_cap_min
        self.dividend_yield = 0
        self.tev = 0

    def get_ticker_info(self) -> yahooquery.Ticker:
        """Returns the ticker info

        :return: Ticker info
        :rtype: yahooquery.Ticker
        """
        ticker: yahooquery.Ticker = yahooquery.Ticker(self.symbol)
        self.fill_ticker_info(ticker)

        if isinstance(self.ticker_info.asset_profile, str):
            return None

        if not self.valid_information_dict():
            return None

        self.logger.debug(self.symbol)

        return ticker

    def valid_ticker_data(self) -> bool:
        """Gets ticker data from the Ticker object

        :return: Returns True if the ticker data is valid
        :rtype: bool
        """
        if not self.valid_information_dict():
            return False

        if not self.valid_industry():
            return False

        if not self.valid_ebit():
            return False

        if not self.valid_ticker_info():
            return False

        return True

    def fill_ticker_info(self, ticker: yahooquery.Ticker) -> None:
        """Fills the variable ticker_info

        :param ticker: Ticker object
        :type ticker: yahooquery.Ticker
        """
        builder = TickerInfoBuilder(symbol=self.symbol, ticker=ticker)
        self.ticker_info: TickerInfo = builder.build()

    def valid_ticker_info(self) -> bool:
        """Validates if the variable ticker_info has informations

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ticker_info is not None

    def valid_information_dict(self) -> bool:
        """Validates if the variable ticker_info has informations

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ticker_info.all_modules_found

    def valid_industry(self) -> bool:
        """Validates if the industry of the company is valid
        for this method of calculation

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ticker_info.industry not in ['Insurance—Diversified', 'Banks—Regional']

    def valid_ebit(self) -> bool:
        """Validates if the variable ebit is valid

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ticker_info.ebit >= self.ebit_min

    def valid_market_cap(self) -> bool:
        """Validates if the variable market_cap is valid

        :return: Boolean with the result of the validation
        :rtype: bool
        """
        return self.ticker_info.market_cap >= self.market_cap_min

    def calculate_tev(self) -> float:
        """Calcullates the current tev (total enterprise value) and returns it

        :return: Total enterpris value
        :rtype: float
        """
        self.tev = self.ticker_info.total_stockholder_equity + self.ticker_info.total_debt
        return self.tev

    def calculate_earning_yield(self) -> float:
        """Calculates the current earning yield of the company

        :return: Current earning yeld
        :rtype: float
        """
        return round((self.ticker_info.ebit / self.tev), 2)
