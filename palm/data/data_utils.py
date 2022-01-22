from datetime import datetime, timedelta
import json
from tqdm import tqdm
import os

import numpy as np
import pandas as pd

from polygon import RESTClient

from ..asset.equity import PolygonEquity
from .polygon_eod import PolygonEOD

def pull_polygon_eod(symbols,
                        start_date: datetime,
                        end_date: datetime, 
                        api_key = None, 
                        show_progress: bool = True):
    ## TODO: Currently doesn't support getting datasets which don't have
    ## survivor bias. Should handle the case where we don't have the complete data.
    ## and fill it with NaN as a substitute for "unavailable".

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
        environment_key = os.getenv('POLYGON_IO_API_KEY')
        if environment_key is None:
            raise RuntimeError("Polygon Api Key is not provided and cannot find environment variable: POLYGON_IO_API_KEY")
        else:
            api_key = environment_key

    loader = tqdm(symbols) if show_progress else symbols
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    eod_data = {}
    with RESTClient(api_key) as client:
        for symbol in loader:
            response = client.stocks_equities_aggregates(symbol, 1, 'day', start_date, end_date)
            if response.status == 'OK':
                eod_data[symbol] = pd.DataFrame(response.results)
                ## Convert from unix millisecond time stamp to date and time.
                eod_data[symbol]['datetime'] = eod_data[symbol]['t'].apply(lambda timestamp: datetime.fromtimestamp(timestamp/1000.0)+timedelta(hours = 8))
                eod_data[symbol].index = pd.DatetimeIndex(eod_data[symbol]['datetime'])

    return PolygonEOD(eod_data)

def trim_daily_eod_data(daily_eod: dict):
    """
    Takes a dictionary of EOD data and returns a trimmed
    version, where only dataframes which have the maximum
    number of rows is returned.

    Parameters
    ----------
    daily_eod: dict[Dataframes]

    Returns
    ----------
    trimmed_eod: dict[Dataframes]
    """

    max_rows = get_max_rows(daily_eod)
    trimmed_eod = {}
    has_max_rows = lambda OHLCV_data: len(OHLCV_data)==max_rows
    for symbol in daily_eod.keys():
        if has_max_rows(daily_eod[symbol]):
            trimmed_eod[symbol] = daily_eod[symbol]

    return trimmed_eod

def get_max_rows(daily_eod: dict):
    """
    Parameters
    -----------
    daily_eod: dict[Dataframes]
        - Each dataframe assuming it is OHLCV.

    Returns
    ----------
    max_rows: int
        - The maximum number of rows. 
    """

    num_rows = {}
    for symbol in daily_eod.keys():
        N = len(daily_eod[symbol])
        if (N not in num_rows.keys()):
            num_rows[N] = 1
        else:
            num_rows[N] += 1

    max_rows = -1
    for row_count in num_rows.keys():
        if num_rows[row_count] > max_rows:
            max_rows = row_count
        else:
            continue

    return max_rows

def get_first_symbol(dataframe_dict: dict):
    return list(dataframe_dict.keys())[0]

def union_of_timestamps(dataframes: dict):
    """
    Gets the union of all time stamps which index the dataframes.
    Example usage is creating price matrix for assets which 
    are missing values.

    Returns
    -------
    union_indices: pd.Index
        union of all indices from dict of dataframes
    """
    first_symbol = get_first_symbol(dataframes)
    union_indices = dataframes[first_symbol].index

    for symbol in dataframes.keys():
        if (symbol == first_symbol):
            continue
        else:
            union_indices = union_indices.union(dataframes[symbol].index)

    return union_indices


def all_indices_overlap(dataframes: dict):
    """
    Verifies whether the indices in a set of dataframes 
    overlaps.
    """
    all_overlap = True
    first_symbol = get_first_symbol(dataframes)
    previous_indices = data_frames[first_symbol].index

    for symbol in dataframes.keys():
        if (symbol == first_symbol):
            continue
        else:
            current_indices = dataframes[symbol].index 

            all_overlap = all_overlap and (current_indices == previous_indices).all()
            previous_indices = current_indices

    return all_overlap

def read_listings_from_json(equity_listing_filename: str):
    """
    Reads a equity metadata from a json file and
    returns a list of Polygon Equity Objects.

    Parameters
    ----------
    listings_json_file: str
        - Json file with raw representation of Polygon Equity

    Returns
    -------
    listings: list[PolygonEquity]
    """

    if not equity_listing_filename.endswith(".json"):
        raise RuntimeError("Need a json file for equity_listing_filename.")

    with open(equity_listing_filename) as in_file:
        data = json.load(in_file)

    equities = []
    for raw in data:
        equities.append(PolygonEquity(raw)) 

    return equities