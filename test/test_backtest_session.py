import pandas as pd
import pytest

import palm as pm

@pytest.fixture
def eod_data():

    data = {}
    data["AAPL"] = pd.read_csv("sample_data/AAPL-Sample-Data.csv", index_col=0)
    data["MSFT"] = pd.read_csv("sample_data/MSFT-Sample-Data.csv", index_col=0)

    return pm.EquityEOD(pm.polygon_symbol_indexed_to_OHCLV_indexed(data))

