from datetime import datetime
import json
from tqdm import tqdm

import numpy as np

import alpaca_trade_api as tradeapi 
from ..asset.equity import PolygonEquity


def pull_alpaca_eod(equity_listings: list, start_date: datetime, 
                    end_date: datetime, 
                    show_progress: bool = True):
    """
    Pulls equity listings from Alpaca trade api which are listed
    in equity_listings.

    The dates pulled are for equities whose listing date is before the start date
    and were last updated after the end_date. 

    Example
    --------
    import datetime

    small_cap_listings = read_listings_from_json(<filename>)
    symbols, dict_of_OHLCV = pull_alpaca_eod(   
                                datetime(2015,1,1), 
                                datetime(2016,31,31)),
                                small_cap_listings)

    Parameters
    -----------
    start_date: date_time object
        - defaulted to (PST timezone).
    end_date: date_time object
        - defaulted to (PST timezone).
    equity_listings: list[PolygonEquity]
        - List of Polygon Equity objects.
    show_progress: bool
        - Defaults to true

    Returns
    --------
    dict_of_OHLCV: dictionary of Dataframes
        - Set of dataframes.

    """

    in_window = lambda equity: (equity.listdate < start_date) and (equity.active)
    active_in_window = list(filter(in_window, equity_listings))

    daily_eod = {}
    loader = tqdm(active_in_window) if show_progress else active_in_window
    api = tradeapi.REST()
    for equity in loader:
        try:
            OHLCV = api.polygon.historic_agg_v2(equity.symbol, 1, 'day', _from = start_date, to = end_date).df
        except:
            continue

        daily_eod[equity.symbol] = OHLCV.sort_index()

    return daily_eod

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