import pytest

import pandas as pd
from palm.data import polygon_symbol_indexed_to_OHCLV_indexed, EquityEOD


@pytest.fixture
def eod_data():

    data = {}
    data["AAPL"] = pd.read_csv("sample_data/AAPL-Sample-Data.csv")
    data["MSFT"] = pd.read_csv("sample_data/MSFT-Sample-Data.csv")

    return data


def test_polygon_eod(eod_data):

    polygon_data = EquityEOD(polygon_symbol_indexed_to_OHCLV_indexed(eod_data))
    T, N = polygon_data.shape
    assert T == 178
    assert N == 2

    symbols = set(["AAPL", "MSFT"])
    assert set(polygon_data.symbols) == symbols


## TODO need to test open, close, volume and other fields needed to satisfy equity EOD.
