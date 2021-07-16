from __future__ import absolute_import

import os
import sys
import unittest
import logging
from unittest import mock
import yahooquery

try:
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
    )
except:
    raise

from src import stocks_greenblat_magic_formula as green
from src.stocks_greenblat_magic_formula import logging


def scenario_logger():
    logger = logging.getLogger(__name__)
    return logger
