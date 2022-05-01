from palm.backtestsession import BacktestSubscribeSession
from palm.backtestsession.backtestsession import Strategy
from palm.data.equity_eod import EquityEOD
import pytest

import pandas as pd

from palm.data import polygon_symbol_indexed_to_OHCLV_indexed

@pytest.fixture
def eod_data():

    data = {}
    data["AAPL"] = pd.read_csv("sample_data/AAPL-Sample-Data.csv", index_col=0)
    data["MSFT"] = pd.read_csv("sample_data/MSFT-Sample-Data.csv", index_col=0)

    return EquityEOD(polygon_symbol_indexed_to_OHCLV_indexed(data))

def test_StrategyWithNoSymbols_BacktestSubscribeSessionConstructionGThrowsValueError(eod_data):
    class TestStrategy(Strategy):
        def __init__(self):
            count = 1

        def on_update(self, historical_data, context, trader):
            return

    test_strategy = TestStrategy()
    error_caught = False
    try:
        expected_failed_session = BacktestSubscribeSession(
            test_strategy,
            eod_data, 
            look_back_days=30
        )
    except ValueError:
        error_caught = True

    assert error_caught


def test_StrategyWithoutSymbolList_BacktestSubscribeSessionConstructionThrowsValueError(eod_data):

    class TestStrategy(Strategy):
        def __init__(self):
            self.symbols = "SPY"

        def on_update(self, historical_data, context, trader):
            return

    test_strategy = TestStrategy()
    error_caught = False
    try:
        expected_failed_session = BacktestSubscribeSession(
            test_strategy, 
            eod_data,
            look_back_days=30
        )
    except ValueError:
        error_caught = True

    assert error_caught


def test_StrategyWithEmptySymbolList_BacktestSubscribeSessionConstructionThrowsValueError(eod_data):

    class TestStrategy(Strategy):
        def __init__(self):
            self.symbols = []

    test_strategy = TestStrategy()
    error_caught = False
    try:
        expected_failed_session = BacktestSubscribeSession(
            test_strategy, 
            eod_data,
            look_back_days=30
        )
    except ValueError:
        error_caught = True

    assert error_caught


def test_StrategyWithValidSymbolList_BacktestSubscribeSessionConstructionSucceedsWithoutError(eod_data):

    class TestStrategy(Strategy):
        def __init__(self):
            self.symbols = ["AAPL", "MSFT"]

    test_strategy = TestStrategy()
    error_caught = False
    try:
        expected_failed_session = BacktestSubscribeSession(
            test_strategy, 
            eod_data,
            look_back_days=30
        )
    except ValueError:
        error_caught = True

    assert not error_caught
