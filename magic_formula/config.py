from __future__ import absolute_import

import logging
import logging.handlers
import os
import json
import sys
import argparse
from argparse import Namespace


def get_config(config_file: str = os.path.join(os.path.dirname(__file__), 'config.json')) -> dict:
    """Returns the configuration from a config file

    :param config_file: json file with the configurations
    :type config_file: str
    :return: dictionary with the configurations
    :rtype: dict
    """
    with open(config_file) as file:
        config = json.load(file)

    return config


def set_logger(logger: logging.Logger = logging.Logger(__name__), log_file_name: str = 'stocks.log',
               log_level: str = 'DEBUG') -> logging.Logger:
    """Sets the logger configuration

    :param logger: Logger variable
    :type logger: logging.Logger
    :param log_file_name: name of the log file, defaults to 'stocks.log'
    :type log_file_name: str, optional
    :return: logger object
    :rtype: logging.Logger
    """
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
        action='store', type=int, default=10
    )

    parser.add_argument(
        '-o', '--output_folder', help='Path for output folder',
        action='store', type=str, default=None
    )

    parser.add_argument(
        '-i', '--index', help='Bovespa index (BRX100, IBOV, SMALL, IDIV)',
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
        type=int, default=15
    )

    parser.add_argument(
        '-d', '--database', help='Send information to a database[POSTGRESQL].', action='store',
        type=str
    )

    options = parser.parse_args(args)
    return options
