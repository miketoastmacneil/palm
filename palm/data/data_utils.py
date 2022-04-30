from datetime import datetime, timedelta
import json
from tqdm import tqdm
import os

import numpy as np
import pandas as pd

from polygon import RESTClient

from .equity_eod import EquityEOD


def pull_polygon_eod(
    symbols,
    start_date: datetime,
    end_date: datetime,
    api_key=None,
    show_progress: bool = False,
):
    """
    Pulls EOD data from polygons API.

    Parameters:
    -----------
    symbols: List[str], list of symbols to get data on.
    start_date: datetime, date from which to pull data.
    end_date: datetime, date to which to pull data.
    api_key: str, Polygon io api key, if none looks for
        and environment variable named "POLYGON_IO_API_KEY",
        otherwise throws an error.

    Returns:
    --------
    eod_data: dict[DataFrame], dictionary of dataframes returned
        from polygon REST request.

        The dictionary of dataframes is indexed by the symbols requested. The columns
        of each dataframe follow the convention from the polygon
        stock historical aggregates docs.
        ('v', 'vw', 'o', 'c', 'h', 'l', 't', 'n')

        The only difference from the REST response is the `t` field is transformed
        from a Unix Msec timestamp to a datetime object.

        If the historical record of the company is shorter than requested,
        the full available history is returned.
    """
    if (type(symbols) is not list) and (type(symbols) is not str):
        raise RuntimeError("Symbols expected to be a list or string.")

    if type(symbols) is str:
        symbols = [symbols]

    if api_key is None:
        environment_key = os.getenv("POLYGON_IO_API_KEY")
        if environment_key is None:
            raise RuntimeError(
                "Polygon Api Key is not provided and cannot find environment variable: POLYGON_IO_API_KEY"
            )
        else:
            api_key = environment_key

    loader = tqdm(symbols) if show_progress else symbols
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    eod_data = {}
    with RESTClient(api_key) as client:
        for symbol in loader:
            response = client.stocks_equities_aggregates(
                symbol, 1, "day", start_date, end_date
            )
            if response.status == "OK":
                try:
                    result = response.results
                except AttributeError:
                    print(f"No results found for {symbol}, continuing")
                    break
                eod_data[symbol] = pd.DataFrame(response.results)
                ## Convert from unix millisecond time stamp to date and time.
                eod_data[symbol]["datetime"] = eod_data[symbol]["t"].apply(
                    lambda timestamp: datetime.fromtimestamp(timestamp / 1000.0)
                    + timedelta(hours=8)
                )
                eod_data[symbol].index = pd.DatetimeIndex(eod_data[symbol]["datetime"])

    return EquityEOD(polygon_symbol_indexed_to_OHCLV_indexed(eod_data))


def polygon_symbol_indexed_to_OHCLV_indexed(data: dict):

    OHLCV_indexed = {}
    OHLCV_indexed["open"] = {}
    OHLCV_indexed["close"] = {}
    OHLCV_indexed["high"] = {}
    OHLCV_indexed["low"] = {}
    OHLCV_indexed["volume"] = {}
    ## Open
    for symbol in data.keys():
        OHLCV_indexed["open"][symbol] = data[symbol]["o"]
        OHLCV_indexed["close"][symbol] = data[symbol]["c"]
        OHLCV_indexed["high"][symbol] = data[symbol]["h"]
        OHLCV_indexed["low"][symbol] = data[symbol]["l"]
        OHLCV_indexed["volume"][symbol] = data[symbol]["v"]

    OHLCV_indexed["open"] = pd.DataFrame(OHLCV_indexed["open"])
    OHLCV_indexed["close"] = pd.DataFrame(OHLCV_indexed["close"])
    OHLCV_indexed["high"] = pd.DataFrame(OHLCV_indexed["high"])
    OHLCV_indexed["low"] = pd.DataFrame(OHLCV_indexed["low"])
    OHLCV_indexed["volume"] = pd.DataFrame(OHLCV_indexed["volume"])

    return OHLCV_indexed
