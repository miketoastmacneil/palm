from datetime import datetime
from palm.broker.simulated_broker import SimulatedBroker
from palm.context.daily_bar_context import ContextEOD

import numpy as np
import pandas_datareader as pdr

from palm.data.yahoo_eod import YahooEOD

start_date = datetime(2019, 1, 1)
end_date = datetime(2020, 10, 10)

symbol_list = [
    "BAC",
    "BK",
    "C",
    "CFG",
    "CMA",
    "COF",
    "FITB",
    "GS",
    "JPM",
    "KEY",
    "MS",
    "MTB",
    "PBCT",
    "PNC",
    "STT",
    "USB",
    "WFC",
    "ZION",
]

src_data = pdr.data.DataReader(symbol_list, "yahoo", start_date, end_date)

eod_data = YahooEOD(src_data)
context = ContextEOD(eod_data)

broker = SimulatedBroker(context, 10000)
