"""Module to take info from yahoo finance and status invest"""
# TODO: Change the export for database (postgresql)
# TODO: Change into a service
# TODO: Include possibilite to use all bovespa stocks
# TODO: Include the possibility to read other specific indexes
# TODO: Improve tests
# TODO: create github actions for the tests
# TODO: Change the filters to make then optional so the formula is closer \
# to pure magic formula
# TODO: Improve the readme.md
# TODO: Improve the sheet for better undestanding the output
# TODO: Separate into different modules so the code is cleaner
# TODO: Improve the coverage of the tests

import datetime
import logging
import logging.handlers
import os
import threading

import numpy as np
import pandas
from pandas import DataFrame
import sqlalchemy

from config import get_config
from config import set_logger
from config import get_arguments
from status_invest import get_ticker_roic_info, get_ibrx_info
from magic_formula import MagicFormula

__VERSION__ = '0.1.0'

MAX_NUMBER_THREADS = 10
XLSX_PATH = os.path.join(os.getcwd(), 'xlsx_files/')


def main(logger: logging.Logger = logging.getLogger(__name__)):
    """Main method """
    global MAX_NUMBER_THREADS
    # TODO: Integrate CLI to the system
    options = get_arguments()
    if options.version:
        show_version()

    if not os.path.exists(XLSX_PATH):
        os.makedirs(XLSX_PATH)

    logger = set_logger(logger)
    config = get_config()
    MAX_NUMBER_THREADS = config.get('MAX_NUMBER_THREADS', MAX_NUMBER_THREADS)
    roic_index_info = get_ticker_roic_info(
        config['STATUS_INVEST_URL'].format('"')
    )
    stock_tickers = get_ibrx_info(config['BRX10_URL'], logger)
    tickers_df = process_tickers(stock_tickers, roic_index_info, logger)
    tickers_df = sort_dataframe(tickers_df, logger)

    export_dataframe_to_excel(tickers_df, logger, options.qty)
    export_dataframe_to_sql(tickers_df, logger, config["POSTGRESQL_STRING"], options.qty)


def show_version():
    print(f'MagicFormula v{__VERSION__}')
    exit(0)


def export_dataframe_to_excel(tickers_df: pandas.DataFrame, logger: logging.Logger,
    number_of_lines: int = None) -> None:
    """Exportts the ticker dataframe into an excel file

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: None
    """
    excel_file_name = \
        f'{XLSX_PATH}stocks_magic_formula_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx'

    if number_of_lines:
        tickers_df = tickers_df.head(number_of_lines)

    logger.info(f'Exporting data into excel {excel_file_name}')
    tickers_df.to_excel(
        excel_writer=excel_file_name,
        sheet_name='stocks', index=False, engine='openpyxl',
        freeze_panes=(1, 0)
    )


def export_dataframe_to_sql(tickers_df: pandas.DataFrame, logger: logging.Logger, connection_string: str,
    number_of_lines: int = None) -> None:
    """Exportts the ticker dataframe into an postgresql

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: None
    """
    logger.info(f'Exporting data into postgresql.')
    try:
        if number_of_lines:
            tickers_df = tickers_df.head(number_of_lines)

        engine = sqlalchemy.create_engine(connection_string)
        tickers_df.to_sql('magicformula', engine, if_exists='append', index=False)
    except sqlalchemy.exc.OperationalError as error:
        logger.error(f'Error on conection with database {error}')


def sort_dataframe(tickers_df: pandas.DataFrame, logger: logging.Logger) -> pandas.DataFrame:
    """Sorts the dataframe and fill the fields roic_index_number, earning_yield_field, magic_index_field
    Those fields depends on the sorting to be generates

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: None
    :rtype: pandas.DataFrame
    """
    logger.info('Sorting dataframe')
    tickers_df = tickers_df.sort_values('roic', ascending=False)
    
    tickers_df = fill_roic_index_number_field(tickers_df, logger)
    
    tickers_df = tickers_df.sort_values('earning_yield', ascending=True)

    tickers_df = fill_earning_yield_field(tickers_df, logger)
    tickers_df = fill_magic_index_field(tickers_df, logger)

    tickers_df = tickers_df.sort_values('magic_index', ascending=True)

    return tickers_df


def fill_roic_index_number_field(tickers_df: pandas.DataFrame, logger: logging.Logger) -> pandas.DataFrame:
    """Fill the field roic_index_number based on roic field

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: Dataframe with field roic_index_number filled
    :rtype: pandas.DataFrame
    """
    tickers_df['roic_index_number'] = np.arange(tickers_df['roic'].count())

    return tickers_df


def fill_earning_yield_field(tickers_df: pandas.DataFrame, logger: logging.Logger) -> pandas.DataFrame:
    """Fill the field earning_yield_index based on earning_yield field

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: Dataframe with field earning_yield_index filled
    :rtype: pandas.DataFrame
    """
    logger.info('Filling field earning_yield_index')
    tickers_df['earning_yield_index'] = \
        np.arange(tickers_df['earning_yield'].count())

    return tickers_df


def fill_magic_index_field(tickers_df: pandas.DataFrame, logger: logging.Logger) -> pandas.DataFrame:
    """Fill the field magic_index based on earning_yield_index and roic_index_number

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: Dataframe with field magic_index filled
    :rtype: pandas.DataFrame
    """
    tickers_df['magic_index'] = \
        tickers_df['earning_yield_index'] + tickers_df['roic_index_number']

    return tickers_df


def return_earning_yield(symbol: str, df: DataFrame,
                         index: int, roic_index: dict,
                         logger: logging.Logger) -> float:
    """Returns stock earning yield.

    :param symbol: Ticker symbol
    :type symbol: str
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
    stock = MagicFormula(symbol, logger)
    if stock.get_ticker_info() is None:
        return False

    if not stock.get_ticker_data():
        return False

    stock.calculate_tev()
    earning_yield = stock.calculate_earning_yield()

    roic_index_number = roic_index.get(symbol[:-3], '').get('roic_index')
    roic = roic_index.get(symbol[:-3], '').get('roic')
    magic_index = earning_yield + roic_index_number

    if earning_yield > 0:
        logger.debug(f'Inserting ticker: {symbol} on dataframe')

        df.loc[str(index)] = [
            symbol[:-3], magic_index, earning_yield, roic_index_number, roic,
            stock.recommendation_trend[0],
            stock.recommendation_trend[1], stock.current_price,
            stock.regular_market_time, stock.market_cap,
            stock.total_stockholder_equity, stock.ebit, stock.total_debt,
            stock.total_cash,
            stock.shares_outstanding, stock.long_name, stock.short_name
        ]

    return earning_yield


def process_tickers(stock_tickers: set, roic_index: dict,
                    logger: logging.Logger) -> DataFrame:
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

    threads = []
    logger.info('Processing tickers')
    for index, ticker in enumerate(stock_tickers):
        if len(threads) == MAX_NUMBER_THREADS:
            for thread in threads:
                thread.join()
            threads = []

        thread = threading.Thread(
            target=return_earning_yield,
            args=(ticker + '.SA', df, index, roic_index, logger, )
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
