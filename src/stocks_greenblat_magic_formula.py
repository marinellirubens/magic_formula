"""Module to take info from yahoo finance and status invest"""
# TODO: Introduce CLI
# TODO: Change the export for database (postgresql)
# TODO: Change into a service
# TODO: Include possibilite to use all bovespa stocks
# TODO: Include the possibility to read other specific indexes
# TODO: Improve tests
# TODO: create github actions for the tests
# TODO: Change the filters to make then optional so the formula is closer to pure magic formula
# TODO: Improve the readme.md
# TODO: Improve the sheet for better undestanding the output
# TODO: Separate into different modules so the code is cleaner
# TODO: Improve the coverage of the tests


import datetime
import json
import logging
import logging.handlers
import os
import sys
import threading
from collections import namedtuple
from typing import Tuple

import bs4
import numpy as np
import pandas
import requests
import yahooquery
from pandas import DataFrame

from setup import get_config
from setup import set_logger

MAX_NUMBER_THREADS = 10
XLSX_PATH = os.path.join(os.getcwd(), 'xlsx_files/')


def main(logger: logging.Logger = logging.getLogger(__name__)):
    """Main method """
    if not os.path.exists(XLSX_PATH):
        os.makedirs(XLSX_PATH)

    logger = set_logger(logger)
    config = get_config()
    roic_index_info = get_ticker_roic_info(config['STATUS_INVEST_URL'].format('"'))
    stock_tickers = get_ibrx_info(config['BRX10_URL'], logger)
    tickers_df = process_tickers(stock_tickers, roic_index_info, logger)

    logger.info('Sorting dataframe')
    tickers_df = tickers_df.sort_values('roic', ascending=False)
    tickers_df['roic_index_number'] = np.arange(tickers_df['roic'].count())
    tickers_df = tickers_df.sort_values('earning_yield', ascending=True)
    tickers_df['earning_yield_index'] = np.arange(tickers_df['earning_yield'].count())
    tickers_df['magic_index'] = tickers_df['earning_yield_index'] + tickers_df['roic_index_number']
    tickers_df = tickers_df.sort_values('magic_index', ascending=True)

    excel_file_name = f'{XLSX_PATH}stocks_magic_formula_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx'

    logger.info(f'Exporting data into excel {excel_file_name}')
    tickers_df.to_excel(
        excel_writer=excel_file_name,
        sheet_name='stocks', index=False, engine='openpyxl', freeze_panes=(1, 0),
    )


def get_ticker_info(symbol: str, logger: logging.Logger) -> yahooquery.Ticker:
    """Returns the ticker info

    :param symbol: stock ticker
    :type symbol: str
    :param logger: Logger object
    :type logger: logging.Logger
    :return: Ticker info
    :rtype: yahooquery.Ticker
    """
    ticker = yahooquery.Ticker(symbol)
    return ticker


def get_ticker_data(symbol: str, ticker: yahooquery.Ticker) -> Tuple[bool, namedtuple]:
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
    recommendation_trend = get_recomendation_trend(ticker=ticker)

    ebit = all_modules['incomeStatementHistory']['incomeStatementHistory'][0]['ebit']
    key_statistics = all_modules['defaultKeyStatistics']
    balance_sheet = all_modules['balanceSheetHistory']

    ticker_tuple = ticker_info(financial_data, ticker_price,
                               key_statistics, balance_sheet, ebit,
                               recommendation_trend)
    return ticker_tuple


def get_recomendation_trend(ticker: yahooquery.Ticker) -> tuple:
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


def ticker_is_valid(symbol: str, logger: logging.Logger) -> Tuple[bool, namedtuple]:
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
    
    ticker = get_ticker_info(symbol, logger)
    all_modules = ticker.all_modules[symbol]
    if not isinstance(all_modules, dict):
        return False, tuple()

    financial_data = ticker.financial_data[symbol]
    ticker_price = all_modules.get('price', {})
        
    recommendation_trend = get_recomendation_trend(ticker=ticker)

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


def return_earning_yield(symbol: str, tickers: list, df: DataFrame,
                         index: int, roic_index: dict, logger: logging.Logger) -> float:
    """Returns stock earning yield.

    :param symbol: Ticker symbol
    :type symbol: str
    :param tickers: tickers list
    :type tickers: list
    :param df: pandas data frame to be filled
    :type df: DataFrame
    :param index: df index
    :type index: int
    :param roic_index: dictionary with the roic information
    :type roic_index: dict
    :param logger: Logger object
    :type logger: logging.Logger
    :return: Earning yeld of the current stock
    :rtype: float
    """
   
    ticker_valid, ticker_info = ticker_is_valid(symbol, logger)
    if not ticker_valid:
        return False

    total_cash = ticker_info.financial_data['totalCash']
    current_price = ticker_info.financial_data['currentPrice']
    total_debt = ticker_info.financial_data['totalDebt']
    long_name = ticker_info.price.get('longName', '')
    short_name = ticker_info.price.get('shortName', '')
    market_cap = ticker_info.price.get('marketCap', 0)
    regular_market_time = ticker_info.price.get('regularMarketTime', 0)

    shares_outstanding = ticker_info.key_statistics.get('sharesOutstanding', 0)
    if shares_outstanding == 0:
        shares_outstanding = ticker_info.key_statistics.get('impliedSharesOutstanding', 0)

    total_stockholder_equity_patrimonio_liquido = \
        ticker_info.balance_sheet['balanceSheetStatements'][0]['totalStockholderEquity']
    tev = total_stockholder_equity_patrimonio_liquido + total_debt
    ebit = ticker_info.ebit
    earning_yield = round((tev / ebit), 2)

    roic_index_number = roic_index.get(symbol[:-3], '').get('roic_index')
    roic = roic_index.get(symbol[:-3], '').get('roic')
    magic_index = earning_yield + roic_index_number

    if earning_yield > 0:
        logger.debug(f'Inserting ticker: {symbol} on dataframe')

        df.loc[str(index)] = [
            symbol[:-3], magic_index, earning_yield, roic_index_number, roic,
            ticker_info.recommendation_trend[0],
            ticker_info.recommendation_trend[1], current_price, regular_market_time, market_cap,
            total_stockholder_equity_patrimonio_liquido, ebit, total_debt, total_cash,
            shares_outstanding, long_name, short_name
        ]

    return earning_yield


def get_ibrx_info(url: str, logger: logging.Logger) -> set:
    """Returns set with IRX100 index

    :param url: status invest url
    :type url: str 
    :param logger: Logger object
    :type logger: logging.Logger
    :return: set with IRX100 index
    :rtype: set
    """
    logger.info(f'Processing url: {url}')
    
    bs = bs4.BeautifulSoup(requests.get(url, verify=True).content, "html.parser")
    tickers_ibrx100 = set([x.text for x in list(bs.find_all("span", {"class": "ticker"}))])
    
    logger.info(f'Returned {len(tickers_ibrx100)} tickers')
    
    return tickers_ibrx100


def get_ticker_roic_info(url: str) -> dict:
    """Returns ibrx100 index informations

    :param url: status invest url
    :type url: str 
    :return: Dictionary with ibrx100 index informations
    :rtype: dict
    """
    tickers_info = requests.get(url).content

    df: pandas.DataFrame = pandas.read_json(tickers_info)
    df = df.sort_values('roic', ascending=False)
    
    df['roic'] = df['roic'].replace(np.NaN, 0)
    df['roic_index'] = [x for x, y in enumerate(df['roic'].iteritems())]
    
    df = df[['ticker', 'roic_index', 'roic']]
    df.set_index(['ticker'], inplace=True)
    # df.to_excel(
    #     excel_writer=f'{XLSX_PATH}roic_info_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx',
    #     sheet_name='stocks', index=True, engine='openpyxl', freeze_panes=(1, 0),
    # )
    
    return df.to_dict('index')


def process_tickers(stock_tickers: set, roic_index: dict, logger: logging.Logger) -> DataFrame:
    """Process tickers informations and return a pandas Dataframe

    :param stock_tickers: List of the stock tickers
    :type stock_tickers: set
    :param roic_index: List with the roic information
    :type roic_index: dict
    :return: Dataframe with the tickers and financial information
    :rtype: pandas.DataFrame
    """
    logger.info('Creating pandas Df')
    df = pandas.DataFrame(
        columns=[
            'symbol', 'magic_index', 'earning_yield', 'roic_index_number',
            'roic', 'buy_recomendation', 'sell_recomendation', 'current_price',
            'regular_market_time', 'market_cap', 'patrimonio_liquido', 'ebit',
            'total_debt', 'total_cash', 'shares_outstanding', 'long_name',
            'short_name'
        ]
    )

    tickers = []
    threads = []
    logger.info('Processing tickers')
    for index, ticker in enumerate(stock_tickers):
        if len(threads) == MAX_NUMBER_THREADS:
            for thread in threads:
                thread.join()
            threads = []

        thread = threading.Thread(
            target=return_earning_yield,
            args=(ticker + '.SA', tickers, df, index, roic_index, logger, )
        )
        logger.info(f'Processing ticker: {ticker} on thread {thread}')

        thread.daemon = False
        thread.start()
        threads.append(thread)

    if threads:
        for thread in threads:
            thread.join()
        threads = []

    return df


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    main(logger)
