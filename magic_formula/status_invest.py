"""Module to connect on status invest and get informations"""
from __future__ import absolute_import
from datetime import datetime

import io
import logging

import os
import json
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


def check_cache_file(file_name: str = 'cache/request.json') -> dict:
    if not os.path.exists('cache'):
        os.makedirs('cache')

    if not os.path.exists(file_name):
        return {}

    file_time = os.path.getctime(file_name)
    if (datetime.now() - datetime.fromtimestamp(file_time)).days > 1:
        return {}

    with open(file_name) as file:
        json_text = json.load(file)
    return json_text


def write_cache_file(content: dict, file_name: str = 'cache/request.json'):
    if not os.path.exists('cache'):
        os.makedirs('cache')

    with open(file_name, 'w') as file:
        json.dump(content, file)


def get_ticker_roic_info(url: str) -> dict:
    """Returns index informations

    :param url: status invest url
    :type url: str
    :return: Dictionary with index informations
    :rtype: dict
    """
    tickers_info = check_cache_file()
    if not tickers_info:
        tickers_info = requests.get(url, headers=HEADERS).json().get('list', {})
        write_cache_file(tickers_info)

    roic_info_df: pandas.DataFrame = pandas.read_json(json.dumps(tickers_info))

    roic_info_df['roic'] = roic_info_df['roic'].replace(np.NaN, 0)
    roic_info_df['vpa'] = roic_info_df['vpa'].replace(np.NaN, 0)
    roic_info_df['p_l'] = roic_info_df['p_l'].replace(np.NaN, 0)
    roic_info_df['p_vp'] = roic_info_df['p_vp'].replace(np.NaN, 0)
    roic_info_df['dy'] = roic_info_df['dy'].replace(np.NaN, 0)
    roic_info_df['roic_index'] = [x for x, _ in enumerate(iter(roic_info_df['roic']))]

    roic_info_df = roic_info_df[['ticker', 'roic_index', 'roic',
                                 'vpa', 'lpa', 'p_l', 'p_vp', 'dy']]
    roic_info_df.set_index(['ticker'], inplace=True)

    return roic_info_df.to_dict('index')

