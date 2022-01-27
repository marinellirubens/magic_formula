"""Module to test methods from module magic_formula"""
import os
import _pickle as pickle
import sys
import unittest
from unittest import mock
import pandas
import yahooquery

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../magic_formula')))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests')))

from magic_formula import magic_formula_core


class TestMagicFormula(unittest.TestCase):
    """Test class to test MagicFormula"""
    @mock.patch('logging.Logger')
    def setUp(self, logger): # pylint: disable=arguments-differ
        self.logger = logger
        self.wege = magic_formula_core.MagicFormula('WEGE3.SA', logger)
        self.wege.get_ticker_info()

    def test_magic_formula_instance(self):
        """Test if MagicFormula instance is created"""
        self.assertIsInstance(self.wege, magic_formula_core.MagicFormula)
        self.assertEqual(self.wege.symbol, 'WEGE3.SA')
        self.assertIsNotNone(self.wege.ticker_info)

    def test_validate_ticker_info(self):
        """Test if ticker_info is valid"""
        self.assertIsNotNone(self.wege.ticker_info)
        self.assertIsInstance(self.wege.ticker_info, magic_formula_core.TickerInfo)

    def test_valid_recomendation_trend_error(self):
        """Test if recomendation_trend is valid"""
        self.assertIsNotNone(self.wege.ticker_info.recommendation_trend)
        self.assertIsInstance(
            self.wege.ticker_info.recommendation_trend,
            magic_formula_core.RecomenationTrend)
        self.assertIsInstance(self.wege.ticker_info.recommendation_trend.buy_counter, int)
        self.assertIsInstance(self.wege.ticker_info.recommendation_trend.sell_counter, int)

    def test_valid_ticker_info(self):
        """Test mehotd valid_ticker_info"""
        wege = self.wege
        self.assertTrue(wege.valid_ticker_info())
        wege.ticker_info = None
        self.assertFalse(wege.valid_ticker_info())

    def test_valid_industry(self):
        """Test if industry is valid"""
        return_ = self.wege.valid_industry()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)
        self.wege.ticker_info.industry = 'Banks—Regional'

        return_ = self.wege.valid_industry()

        self.assertIsNotNone(return_)
        self.assertFalse(return_)

    def test_valid_information_dict(self):
        """Test if information_dict is valid"""
        return_ = self.wege.valid_information_dict()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)

        self.wege.ticker_info.all_modules_found = False
        return_ = self.wege.valid_information_dict()

        self.assertFalse(return_)
        wege = self.wege
        with mock.patch.object(wege, 'valid_information_dict') as mock_valid_information_dict:
            mock_valid_information_dict.return_value = False
            return_ = wege.get_ticker_info()
            self.assertIsNone(return_)

    def test_get_ticker_info_valid_information_dict_false(self):
        """Test if get_ticker_info returns None when valid_information_dict is False"""
        return_ = self.wege.get_ticker_info()

        self.assertIsNotNone(return_)
        self.assertTrue(return_)

        wege = self.wege
        with mock.patch.object(wege, 'fill_ticker_info'):
            wege.ticker_info.asset_profile = 'teste'
            return_ = wege.get_ticker_info()

            self.assertIsNone(return_)
            self.assertFalse(return_)

    def test_calculate_tev(self):
        """Test if tev is valid"""
        self.wege.calculate_tev()

        self.assertIsNotNone(self.wege.tev)
        self.assertGreater(self.wege.tev, 0)

    def test_calculate_earning_yield(self):
        """Test if earning_yield is valid"""
        self.wege.calculate_tev()
        earning_yield = self.wege.calculate_earning_yield()

        self.assertIsNotNone(earning_yield)
        self.assertGreater(earning_yield, 0)
        self.assertEqual(
            earning_yield,
            (round((self.wege.ticker_info.ebit / self.wege.tev), 2)))

    def test_valid_ticker_data(self):
        """Test method valid_ticker_data"""
        wege = self.wege
        assert wege.valid_ticker_data()

        pre_methods = [
            'valid_ticker_info',
            'valid_information_dict',
            'valid_industry',
            'valid_ebit',
        ]

        for method in pre_methods:
            with mock.patch.object(wege, method) as mock_pre_function:
                mock_pre_function.return_value = False
                assert not wege.valid_ticker_data()

    def test_valid_ebit(self):
        """Validate ebit"""
        wege = self.wege
        wege.ticker_info.ebit = 1
        wege.ebit_min = 0
        assert wege.valid_ebit()

        wege.ebit_min = 1000
        assert wege.valid_ebit() is False

    def test_valid_market_cap(self):
        """Validate market cap"""
        wege = self.wege
        wege.ticker_info.market_cap = 1
        wege.market_cap_min = 0
        assert wege.valid_market_cap()

        wege.market_cap_min = 1000
        assert wege.valid_market_cap() is False


class TestRecomenationTrend(unittest.TestCase):
    """Tests the dataclass RecomenationTrend"""
    def test_recomendation_trend_creation(self):
        """Tests the dataclass RecomenationTrend instance"""
        rec_trend = magic_formula_core.RecomenationTrend(1, 2)

        self.assertIsInstance(rec_trend, magic_formula_core.RecomenationTrend)
        self.assertIsInstance(rec_trend.buy_counter, int)
        self.assertIsInstance(rec_trend.sell_counter, int)


class TestTickerInfoBuilder(unittest.TestCase):
    """Class to build the TickerInfo object"""
    @mock.patch('yahooquery.Ticker')
    @mock.patch('logging.Logger')
    def setUp(self, logger, ticker): # pylint: disable=arguments-differ
        self.symbol = 'WEGE3.SA'
        self.logger = logger
        self.ticker = self.get_ticker_pickles(ticker)
        self.builder = magic_formula_core.TickerInfoBuilder(self.ticker, self.symbol)

    def get_ticker_pickles(self, ticker):
        """Get pickled ticker"""
        ticker_all_modules = pickle.load(open('tests/ticker.all_modules.pkl', 'rb'))
        ticker.all_modules = ticker_all_modules

        ticker_asset_profile = pickle.load(open('tests/ticker.asset_profile.pkl', 'rb'))
        ticker.asset_profile = ticker_asset_profile

        ticker_financial_data = pickle.load(open('tests/ticker.financial_data.pkl', 'rb'))
        ticker.financial_data = ticker_financial_data

        ticker_summary_detail = pickle.load(open('tests/ticker.summary_detail.pkl', 'rb'))
        ticker.summary_detail = ticker_summary_detail

        ticker_recommendation_trend = pickle.load(
            open('tests/ticker.recommendation_trend.pkl', 'rb'))
        ticker.recommendation_trend = ticker_recommendation_trend
        return ticker

    def save_ticker_picles(self) -> None:
        """Method to save the pickles if the methods change over time"""
        ticker: yahooquery.Ticker = yahooquery.Ticker(self.symbol)
        pickles = [
            (ticker.all_modules, 'tests/ticker.all_modules.pkl'),
            (ticker.asset_profile, 'tests/ticker.asset_profile.pkl'),
            (ticker.financial_data, 'tests/ticker.financial_data.pkl'),
            (ticker.summary_detail, 'tests/ticker.summary_detail.pkl'),
            (ticker.recommendation_trend, 'tests/ticker.recommendation_trend.pkl')
        ]

        for object_, file_name in pickles:
            with open(file_name, 'wb') as file:
                pickle.dump(object_, file)

    def test_build(self) -> None:
        pass

    def test_valid_all_modules(self) -> None:
        """Test if all_modules is valid"""
        assert self.builder.valid_all_modules()

    def test_get_all_modules(self) -> None:
        """Test if get_all_modules returns a valid object"""
        ticker = self.ticker
        self.builder.set_ticker(ticker)
        assert self.builder.get_all_modules() == ticker.all_modules.get(self.builder.symbol)
        ticker.all_modules[self.builder.symbol] = 'test'
        assert self.builder.get_all_modules() == {}

    def test_get_industry(self) -> None:
        """Test if get_industry returns a valid object"""
        assert self.builder.get_industry() == 'Specialty Industrial Machinery'

    def test_get_asset_profile(self) -> None:
        """Test if get_asset_profile returns a valid object"""
        assert self.builder.get_asset_profile() == self.ticker.asset_profile[self.builder.symbol]

    def test_get_ticker_price(self) -> None:
        """Tests if get_ticker_price returns a valid object"""
        assert self.builder.get_ticker_price() == self.ticker.all_modules[self.symbol]['price']

    def test_get_financial_data(self) -> None:
        """Tests if get_financial_data returns a valid object"""
        assert self.builder.get_financial_data() == self.ticker.financial_data[self.builder.symbol]

    def test_get_dividend_yield(self) -> None:
        """Test if get_dividend_yield returns a valid object"""
        assert self.builder.get_dividend_yield() == \
            round(self.ticker.summary_detail[self.builder.symbol]['dividendYield'] * 100, 2)

    def test_get_key_statistics(self) -> None:
        """Test if get_key_statistics returns a valid object"""
        assert self.builder.get_key_statistics() == \
            self.ticker.all_modules[self.builder.symbol]['defaultKeyStatistics']

    def test_get_balance_sheet(self) -> None:
        """Test if get_balance_sheet returns a valid object"""
        assert self.builder.get_balance_sheet() == \
            self.ticker.all_modules[self.builder.symbol]['balanceSheetHistory']

    def test_get_summary_detail(self) -> None:
        """Test if get_summary_detail returns a valid object"""
        assert self.builder.get_summary_detail() == \
            self.ticker.summary_detail[self.builder.symbol]

    def test_get_recomendation_trend(self) -> None:
        """Test if get_recomendation_trend returns a valid object"""
        assert isinstance(
            self.ticker.recommendation_trend, pandas.DataFrame)
        
        with mock.patch('pandas.DataFrame.sum') as dataframe:
            dataframe.return_value = (0, 0, 0, 3)
            rec_trend = magic_formula_core.RecomenationTrend(0, 3)
            return_ = self.builder.get_recomendation_trend()
            assert isinstance(return_, magic_formula_core.RecomenationTrend)
            assert rec_trend == return_
            
            dataframe.side_effect = ValueError('test')
            
            with self.assertRaises(ValueError):
                return_ = self.builder.get_recomendation_trend()
                assert magic_formula_core.RecomenationTrend(0, 3) == return_
            

    def test_get_ebit(self) -> None:
        pass

    def test_get_market_cap(self) -> None:
        pass

    def test_get_total_cash(self) -> None:
        pass

    def test_get_current_price(self) -> None:
        pass

    def test_get_total_debt(self) -> None:
        pass

    def test_get_long_name(self) -> None:
        pass

    def test_get_short_name(self) -> None:
        pass

    def test_get_regular_market_time(self) -> None:
        pass

    def test_get_shares_outstanding(self) -> None:
        pass

    def test_get_total_stockholder_equity(self) -> None:
        pass
