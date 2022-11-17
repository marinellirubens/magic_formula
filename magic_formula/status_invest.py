"""Module to connect on status invest and get informations"""
from __future__ import absolute_import

import io
import logging

import bs4
import numpy as np
import pandas
import requests


HEADERS = {
    'authority': 'statusinvest.com.br',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

def get_ibrx_info(url: str, logger: logging.Logger) -> set:
    """Returns set with index tickers

    :param url: status invest url
    :type url: str
    :param logger: Logger object
    :type logger: logging.Logger
    :return: set with index tickers
    :rtype: set
    """
    logger.info(f'Processing url: {url}')
    request_content = requests.get(url, verify=True, headers=HEADERS).content
    beatiful_soup = bs4.BeautifulSoup(request_content, "html.parser")
    tickers_ibrx100 = \
        set([x.text for x in list(beatiful_soup.find_all("span", {"class": "ticker"}))])

    logger.info(f'Returned {len(tickers_ibrx100)} tickers')

    return tickers_ibrx100


def get_ticker_roic_info(url: str) -> dict:
    """Returns index informations

    :param url: status invest url
    :type url: str
    :return: Dictionary with index informations
    :rtype: dict
    """

    tickers_info = requests.get(url, headers=HEADERS).content

    roic_info_df: pandas.DataFrame = pandas.read_json(io.StringIO(tickers_info.decode('utf-8')))
    roic_info_df = roic_info_df.sort_values('roic', ascending=False)

    roic_info_df['roic'] = roic_info_df['roic'].replace(np.NaN, 0)
    roic_info_df['roic_index'] = [x for x, y in enumerate(roic_info_df['roic'].iteritems())]

    roic_info_df = roic_info_df[['ticker', 'roic_index', 'roic', 'vpa', 'lpa', 'p_L', 'p_VP', 'dy']]
    roic_info_df.set_index(['ticker'], inplace=True)

    return roic_info_df.to_dict('index')
