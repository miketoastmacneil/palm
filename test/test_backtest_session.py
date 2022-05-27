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

