"""Module to handle configurations"""
from __future__ import absolute_import

import logging
import logging.handlers
import json
import os
import sys
import argparse
from argparse import Namespace


CONFIG = {
    "BRX100_URL": "https://statusinvest.com.br/indices/indice-brasil-100",
    "SMALL_URL": "https://statusinvest.com.br/indices/indice-small-cap",
    "IBOV_URL": "https://statusinvest.com.br/indices/ibovespa",
    "IDIV_URL": "https://statusinvest.com.br/indices/indice-dividendos",
    "MLCX_URL": "https://statusinvest.com.br/indices/indice-midlarge-cap",
    "IGCT_URL": "https://statusinvest.com.br/indices/indice-de-governanca-corporativa-trade",
    "ITAG_URL": "https://statusinvest.com.br/indices/indice-de-acoes-com-tag-along-diferenciado",
    "IBRA_URL": "https://statusinvest.com.br/indices/indice-brasil-amplo",
    "IGNM_URL":
        "https://statusinvest.com.br/indices/indice-de-governanca-corporativa-–-novo-mercado",
    "IMAT_URL": "https://statusinvest.com.br/indices/indice-de-materiais-basicos",
    "STATUS_INVEST_URL": ("https://statusinvest.com.br/category/advancedsearchresultpaginated?search=%7B%22Sector%22%3A%22%22%2C%22SubSector%22%3A%22%22%2C%22Segment%22%3A%22%22%2C%22my_range%22%3A%22-20%3B100%22%2C%22forecast%22%3A%7B%22upsidedownside%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22estimatesnumber%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22revisedup%22%3Atrue%2C%22reviseddown%22%3Atrue%2C%22consensus%22%3A%5B%5D%7D%2C%22dy%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_l%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22peg_ratio%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_vp%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margembruta%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemliquida%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22ev_ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividaliquidaebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividaliquidapatrimonioliquido%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_sr%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_capitalgiro%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_ativocirculante%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roe%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roic%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezcorrente%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22pl_ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22passivo_ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22giroativos%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22receitas_cagr5%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lucros_cagr5%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezmediadiaria%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22vpa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lpa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22valormercado%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%7D&orderColumn=&isAsc=&page=0&take=621&CategoryType=1"),
    "POSTGRESQL_STRING": "postgresql+psycopg2://postgres:example@0.0.0.0/fmsdeinvestimento"
}


def get_config(config_file: str = '') -> dict:
    """Returns the configuration from a config file

    :param config_file: json file with the configurations
    :type config_file: str
    :return: dictionary with the configurations
    :rtype: dict
    """
    if not config_file:
        return CONFIG

    with open(config_file, encoding='UTF-8') as file:
        config = json.load(file)

    return config


def set_logger(logger: logging.Logger = logging.Logger(__name__), log_file_name: str = 'logs/stocks.log',
               log_level: str = 'DEBUG') -> logging.Logger:
    """Sets the logger configuration

    :param logger: Logger variable
    :type logger: logging.Logger
    :param log_file_name: name of the log file, defaults to 'logs/stocks.log'
    :type log_file_name: str, optional
    :return: logger object
    :rtype: logging.Logger
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - (%(threadName)-10s) - %(levelname)s - %(message)s')
    handler = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=1024 * 1000,
                                                   backupCount=10)
    buff_handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(formatter)
    buff_handler.setFormatter(formatter)

    logger.setLevel(log_level)
    logger.addHandler(handler)
    logger.addHandler(buff_handler)

    return logger


def get_arguments(args: list = sys.argv[1:]) -> Namespace:
    """Parse argument on command line execution

    :param args: arguments to be parsed
    :return: returns the options parsed
    """
    parser = argparse.ArgumentParser(description='Parses command.')
    parser.add_argument(
        '-V', '--version', help='Show program version',
        action='store_true'
    )

    parser.add_argument(
        '-t', '--threads', help='Max Number of threads',
        action='store', type=int, default=15
    )

    parser.add_argument(
        '-o', '--output_folder', help='Path for output folder',
        action='store', type=str, default=None
    )

    parser.add_argument(
        '-i', '--index', help='''Bovespa indexes
        (BRX100, IBOV, SMALL, IDIV, MLCX, IGCT, ITAG, IBRA, IGNM, IMAT, ALL)
        BRX100 - Indice IBRX100
        IBOV - IBOVESPA
        SMALL - Indice de Small Cap
        IDIV - Indice de Dividendos
        MLCX - Indice de Mid-Large Cap
        IGCT - Indice de Governança Corporativa
        ITAG - Indice de Ações com Tag Along diferenciado
        IBRA - Indice Brasil Amplo
        IGNM - Indice de Governança Corporativa - Novo Mercado
        IMAT - Indice de Materiais Basicos
        ALL - Todos os Indices anteriores
        ''',
        action='store', type=str, default=["BRX100"], nargs="+"
    )

    parser.add_argument(
        '-ll', '--log_level', help='Log level',
        action='store', type=str, default="INFO"
    )

    parser.add_argument(
        '-e', '--ebit', help='Minimun ebit to be considered',
        action='store', type=int, default=1
    )

    parser.add_argument(
        '-m', '--market_cap', help='Minimun market cap', action='store', type=int,
        default=0
    )

    parser.add_argument(
        '-q', '--qty', help='Quantity of stocks to be exported.', action='store',
        type=int, default=150
    )

    parser.add_argument(
        '-d', '--database', help='Send information to a database[POSTGRESQL].', action='store',
        type=str
    )

    parser.add_argument(
        '-f', '--format', help='Format to be export [EXCEL, JSON].', action='store',
        type=str, default='EXCEL'
    )

    parser.add_argument(
        '-l', '--list_tickers', help='List stocks instead of using the indexes.',
        action='store', type=str, default=[], nargs="+"
    )

    parser.add_argument(
        '-lf', '--list_tickers_file', help='List stocks file, a text file with a ticker by line.',
        action='store', type=str
    )

    parser.add_argument(
        '-ri', '--roic_ignore', help='Option to ignore roic index and use only EY index',
        action='store_true', default=False
    )

    parser.add_argument(
        '-gpl', '--graham_max_pl', help='Maximum pl for graham formula.[Default: 15]',
        action='store', type=float, default=15
    )

    parser.add_argument(
        '-gpvp', '--graham_max_pvp', help='Maximum pvp for graham formula.[Default: 1.5]',
        action='store', type=float, default=1.5
    )

    options = parser.parse_args(args)
    return options
