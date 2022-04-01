"""Module to take info from yahoo finance and status invest"""
from __future__ import absolute_import

import datetime
import logging
import logging.handlers
import os
import sys
import threading
from argparse import Namespace
from enum import Enum

import numpy as np
import pandas
import sqlalchemy
from pandas import DataFrame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from magic_formula.config import get_config
from magic_formula.config import get_arguments
from magic_formula.config import set_logger
from magic_formula.magic_formula_core import MagicFormula
from magic_formula.status_invest import get_ibrx_info
from magic_formula.status_invest import get_ticker_roic_info


__VERSION__ = '1.0.3'

MAX_NUMBER_THREADS = 10
XLSX_PATH = os.path.join(os.getcwd(), 'xlsx_files/')
POSSIBLE_INDEXES = ['BRX100', 'IBOV', 'SMALL', 'IDIV',
                    'MLCX', 'IGCT', 'ITAG', 'IBRA', 'IGNM', 'IMAT']


class DataframColums(Enum):
    """Enum to contain the columns of the dataframe"""
    EXCEL_DF_COLUMNS = [
        'symbol',
        'roic',
        'current_price',
        'dividend_yield',
        'market_cap',
        'patrimonio_liquido',
        'ebit',
        'total_debt',
        'total_cash',
        'shares_outstanding',
        'long_name',
        'short_name',
        'regular_market_time',
        'buy_recomendation',
        'sell_recomendation',
        'earning_yield_index',
        'magic_index',
        'earning_yield',
        'roic_index_number',
    ]
    EXCEL_DF_COLUMNS_NAMES = [
        'symbol',
        'roic',
        'current_price',
        'dividend_yield (%)',
        'market_cap',
        'net_worth',
        'ebit',
        'total_debt',
        'total_cash',
        'shares_outstanding',
        'long_name',
        'short_name',
        'regular_market_time',
        'buy_recomendation',
        'sell_recomendation',
        'earning_yield_index',
        'magic_index',
        'earning_yield',
        'roic_index_number',
    ]
    PROCESS_TICKERS_COLUMNS = [
        'symbol', 'magic_index', 'earning_yield', 'roic_index_number',
        'roic', 'buy_recomendation', 'sell_recomendation', 'current_price',
        'regular_market_time', 'market_cap', 'patrimonio_liquido', 'ebit',
        'total_debt', 'total_cash', 'shares_outstanding', 'long_name',
        'short_name', 'dividend_yield'
    ]


def main() -> None:
    """Main method

    :return: None
    """
    global MAX_NUMBER_THREADS
    global XLSX_PATH
    options = get_arguments()
    if options.version:
        show_version()

    if options.output_folder:
        if not os.path.exists(options.output_folder):
            raise Exception('Folder informed must exist already, ' + \
                            f'folder {options.output_folder} does not exists.')

        XLSX_PATH = options.output_folder

    if not os.path.exists(XLSX_PATH):
        os.makedirs(XLSX_PATH)

    logger = logging.getLogger(__name__)
    logger = set_logger(logger, log_level=options.log_level)
    config = get_config()

    stock_tickers, options.index = get_tickers_list(options, logger, config)

    MAX_NUMBER_THREADS = options.threads
    roic_index_info = get_ticker_roic_info(
        config['STATUS_INVEST_URL'].format('"')
    )

    tickers_df = process_tickers(stock_tickers, roic_index_info, logger, options)
    tickers_df = sort_dataframe(tickers_df, logger, options.roic_ignore)

    export_dataframe_to_excel(tickers_df, logger, options.qty, options.index)
    if options.database:
        if options.database not in ['POSTGRESQL']:
            logger.error(f'Option {options.database} invalid for database.')
            sys.exit(1)
        export_dataframe_to_sql(tickers_df, logger, config["POSTGRESQL_STRING"], options.qty)


def get_tickers_list(options: Namespace, logger: logging.Logger, config: dict) -> tuple:
    """Get list of tickers and indexes

    :param options: Arguments from command line
    :type options: Namespace
    :param logger: Logger
    :type logger: logging.Logger
    :param config: Config dict
    :type config: dict
    :return: Tuple with tickers and indexes
    :rtype: tuple
    """
    stock_tickers = set(options.list_tickers)
    if options.list_tickers:
        return stock_tickers, ['LIST',]

    indexes = validate_indexes(options.index, logger)

    stock_tickers = set()
    for index in indexes:
        stock_tickers.update(get_ibrx_info(config[f'{index}_URL'], logger))

    return stock_tickers, indexes


def validate_indexes(indexes: list, logger: logging.Logger) -> None:
    """Validate indexes

    :param indexes: List of indexes
    :type indexes: list
    :param logger: Logger
    :type logger: logging.Logger
    :return: None
    :rtype: None
    """
    if not isinstance(indexes, list):
        indexes = [indexes, ]

    if indexes == ['ALL', ]:
        indexes = POSSIBLE_INDEXES

    if not all(index in POSSIBLE_INDEXES for index in indexes):
        logger.error(f'Option {indexes} invalid for index.')
        sys.exit(1)

    return indexes


def show_version() -> None:
    """Prints program version

    :return: None
    """
    print(f'MagicFormula v{__VERSION__}')
    sys.exit(0)


def export_dataframe_to_excel(tickers_df: pandas.DataFrame,
                              logger: logging.Logger,
                              number_of_lines: int = None,
                              indexes: list = None) -> None:
    """Exports the ticker dataframe into an excel file

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :param number_of_lines: Number of lines to be exported on the excel file
    :type number_of_lines: int
    :return: None
    """
    if indexes is None:
        indexes = []

    excel_name = \
        f'stocks_magic_formula_{datetime.datetime.now().strftime("%Y%m%d")}' + \
            f'_{"_".join(indexes)}.xlsx'
    excel_file_name = os.path.join(XLSX_PATH, excel_name)

    if number_of_lines:
        tickers_df = tickers_df.head(number_of_lines)

    logger.info(f'Exporting data into excel {excel_file_name}')

    excel_df = tickers_df[DataframColums.EXCEL_DF_COLUMNS.value]
    excel_df.columns = DataframColums.EXCEL_DF_COLUMNS_NAMES.value

    excel_df.to_excel(
        excel_writer=excel_file_name,
        sheet_name='stocks', index=False, engine='openpyxl',
        freeze_panes=(1, 0)
    )


def export_dataframe_to_sql(tickers_df: pandas.DataFrame, logger: logging.Logger,
                            connection_string: str,
                            number_of_lines: int = None) -> None:
    """Exportts the ticker dataframe into an postgresql

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :param connection_string: Database connection string
    :type connection_string: str
    :param number_of_lines: Number of lines to be exported on the excel file
    :type number_of_lines: int
    :return: None
    """
    logger.info('Exporting data into postgresql.')
    try:
        if number_of_lines:
            tickers_df = tickers_df.head(number_of_lines)

        engine = sqlalchemy.create_engine(connection_string)
        tickers_df.to_sql('magicformula', engine, if_exists='append', index=False)
    except sqlalchemy.exc.OperationalError as error:
        logger.error(f'Error on conection with database {error}')


def sort_dataframe(tickers_df: pandas.DataFrame, logger: logging.Logger,
                   roic_ignore: bool) -> pandas.DataFrame:
    """Sorts the dataframe and fill the fields roic_index_number, earning_yield_field,
    magic_index_field Those fields depends on the sorting to be generates

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: None
    :rtype: pandas.DataFrame
    """
    logger.info('Sorting dataframe')
    tickers_df = tickers_df.sort_values('roic', ascending=False)

    tickers_df = fill_roic_index_number_field(tickers_df, logger, roic_ignore)

    tickers_df = tickers_df.sort_values('earning_yield', ascending=False)

    tickers_df = fill_earning_yield_field(tickers_df, logger)
    tickers_df = fill_magic_index_field(tickers_df, logger)

    tickers_df = tickers_df.sort_values('magic_index', ascending=True)

    return tickers_df


def fill_roic_index_number_field(tickers_df: pandas.DataFrame,
                                 logger: logging.Logger, 
                                 roic_ignore: bool) -> pandas.DataFrame:
    """Fill the field roic_index_number based on roic field

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: Dataframe with field roic_index_number filled
    :rtype: pandas.DataFrame
    """
    logger.debug('Filling field roic_index_number')

    tickers_df['roic_index_number'] = np.arange(tickers_df['roic'].count())
    if roic_ignore:
        tickers_df['roic_index_number'] = [0] * tickers_df['roic'].count()

    return tickers_df


def fill_earning_yield_field(tickers_df: pandas.DataFrame,
                             logger: logging.Logger) -> pandas.DataFrame:
    """Fill the field earning_yield_index based on earning_yield field

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: Dataframe with field earning_yield_index filled
    :rtype: pandas.DataFrame
    """
    logger.debug('Filling field earning_yield_index')
    tickers_df['earning_yield_index'] = \
        np.arange(tickers_df['earning_yield'].count())

    return tickers_df


def fill_magic_index_field(tickers_df: pandas.DataFrame,
                           logger: logging.Logger) -> pandas.DataFrame:
    """Fill the field magic_index based on earning_yield_index and roic_index_number

    :param tickers_df: Dataframe with the stocks information
    :type tickers_df: pandas.DataFrame
    :param logger: Logger object
    :type logger: logging.Logger
    :return: Dataframe with field magic_index filled
    :rtype: pandas.DataFrame
    """
    logger.debug('Filling field magic_index')
    tickers_df['magic_index'] = \
        tickers_df['earning_yield_index'] + tickers_df['roic_index_number']

    return tickers_df


def process_earning_yield_calculation(
        symbol: str, data_frame: DataFrame,
        index: int, roic_index: dict,
        logger: logging.Logger,
        options: Namespace
    ) -> float:
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
    stock: MagicFormula = MagicFormula(symbol, logger, ebit_min=options.ebit,
                                       market_cap_min=options.market_cap)
    if stock.get_ticker_info() is None:
        return False

    if not stock.valid_ticker_data():
        return False

    stock.calculate_tev()
    earning_yield = stock.calculate_earning_yield()

    roic_index_number = roic_index.get(symbol[:-3], '').get('roic_index')
    roic = roic_index.get(symbol[:-3], '').get('roic')
    magic_index = earning_yield + roic_index_number

    if earning_yield > 0:
        logger.debug(f'Inserting ticker: {symbol} on dataframe')

        data_frame.loc[str(index)] = [
            symbol[:-3],
            magic_index,
            earning_yield,
            roic_index_number,
            roic,
            stock.ticker_info.recommendation_trend.buy_counter,
            stock.ticker_info.recommendation_trend.sell_counter,
            stock.ticker_info.current_price,
            stock.ticker_info.regular_market_time,
            stock.ticker_info.market_cap,
            stock.ticker_info.total_stockholder_equity,
            stock.ticker_info.ebit,
            stock.ticker_info.total_debt,
            stock.ticker_info.total_cash,
            stock.ticker_info.shares_outstanding,
            stock.ticker_info.long_name,
            stock.ticker_info.short_name,
            stock.ticker_info.dividend_yield
        ]

    return earning_yield


def process_tickers(stock_tickers: set, roic_index: dict,
                    logger: logging.Logger,
                    options: Namespace) -> DataFrame:
    """Process tickers informations and return a pandas Dataframe

    :param stock_tickers: List of the stock tickers
    :type stock_tickers: set
    :param roic_index: List with the roic information
    :type roic_index: dict
    :return: Dataframe with the tickers and financial information
    :rtype: pandas.DataFrame
    """
    logger.info('Creating pandas Df')
    data_frame = pandas.DataFrame(
        columns=DataframColums.PROCESS_TICKERS_COLUMNS.value
    )

    threads = []
    logger.info('Processing tickers')
    for index, ticker in enumerate(stock_tickers):
        if len(threads) == MAX_NUMBER_THREADS:
            for thread in threads:
                thread.join()
            threads = []

        thread = threading.Thread(
            target=process_earning_yield_calculation,
            args=(ticker + '.SA', data_frame, index, roic_index, logger, options, )
        )
        logger.debug(f'Processing ticker: {ticker} on thread {thread}')

        thread.daemon = False
        thread.start()
        threads.append(thread)

    if threads:
        for thread in threads:
            thread.join()
        threads = []

    return data_frame


if __name__ == '__main__':
    main()
