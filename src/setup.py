import logging
import os
import json
import sys


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


def set_logger(logger: logging.Logger, log_file_name: str = 'stocks.log') -> logging.Logger:
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
    
    logger.setLevel('DEBUG')
    logger.addHandler(handler)
    logger.addHandler(buff_handler)
    
    return logger
