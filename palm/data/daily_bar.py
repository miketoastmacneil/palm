import os
from functools import lru_cache
from pprint import PrettyPrinter
import pytz
from typing import List
import os

from datetime import datetime
import numpy as np
import pandas as pd

from .data_utils import *
from ..asset.equity import *


class DailyBar:
    """
    Offers some facilities for querying EOD bar data.
    """

    @staticmethod
    def pull_from_polygon_and_trim(
        equity_listings: List[PolygonEquity], start_date, end_date
    ):
        """
        Factory Method which pulls listings from polygon and trims them (or cleans them up, some
        only have a few rows).

        Parameters
        ----------
        equity_listings: list[PolygonEquity]
        start_date: date_time
        end_data: date_time
        """
        if end_date <= start_date:
            raise RuntimeError("Start date needs to be before end date.")

        data = pull_alpaca_eod(equity_listings, start_date, end_date)
        trimmed_data = trim_daily_eod_data(data)
        trimmed_listings = [
            listing
            for listing in equity_listings
            if listing.symbol in trimmed_data.keys()
        ]

        return DailyBar(trimmed_listings, trimmed_data, start_date, end_date)

    def __init__(
        self, listings: list, data: dict, start_date: datetime, end_date: datetime
    ):
        self.listings = listings
        self.data_frames = data

        self.symbols = sorted(set(self.data_frames.keys()))
        self._index_to_symbol = {}
        self._symbol_to_index = {}
        for (index, symbol) in enumerate(self.symbols):
            self._index_to_symbol[index] = symbol
            self._symbol_to_index[symbol] = index

        self.start_date = start_date
        self.end_date = end_date

        self.time_stamps = union_of_timestamps(
            self.data_frames
        )  ## TODO, its not clear this is going to give daily
        self.time_stamp_to_index = {}
        for (index, time_stamp) in enumerate(self.time_stamps):
            self.time_stamp_to_index[time_stamp] = index

        self._reindex_time_series()
        self.shape = (len(self.time_stamps), len(self.symbols))

        return

    def _reindex_time_series(self):
        """
        Reindexes the input time series to the largest set of
        each index (see constructor) and fills the values to
        the default of `NaN`.
        """

        for symbol in self.symbols:
            self.data_frames[symbol].reindex(
                self.time_stamps
            )  ## fill_value defaults to `NaN`

    @property
    def index_to_symbol(self):
        return self._index_to_symbol

    @property
    def symbol_to_index(self):
        return self._symbol_to_index

    def get_bar(self, symbol, time_stamp):
        if time_stamp not in self.time_stamp_to_index.keys():
            raise RuntimeError("Time stamp not in dataset range.")

        if symbol not in self.symbols:
            raise RuntimeError("Symbol not found.")

        return self.data_frames[symbol][self.time_stamp_to_index[time_stamp]]

    def get_all_bars(self, time_stamp):
        bars = {}
        for symbol in self.symbols:
            bars[symbol] = self.get_bar(symbol, time_stamp)
        return bars

    def drop_symbol(self, symbol):
        if symbol not in self.symbols:
            raise RuntimeError("Symbol not in dataset.")
        listing_index = -1
        for (index, listing) in enumerate(self.listings):
            if listing.symbol == symbol:
                listing_index = index

        del self.data_frames[symbol]
        self.symbols.remove(symbol)
        self.listings.pop(listing_index)

        return

    def close_prices(self):
        return self._get_field_array("close")

    def open_prices(self):
        return self._get_field_array("open")

    def volume(self):
        return self._get_field_array("volume")

    def high_prices(self):
        return self._get_field_array("high")

    def low_prices(self):
        return self._get_field_array("low")

    @lru_cache(maxsize=6)
    def _get_field_array(self, field_name):
        T, N = self.shape

        out = np.zeros((T, N))

        for (index, symbol) in enumerate(self.symbols):
            out[:, index] = self.data_frames[symbol][field_name].to_numpy()

        return out

    def sample_from_indices(self, indices):
        """
        Samples a set of symbols from their index values
        and returns a new EquityEOD object with just
        those symbols.

        Example usage is clustering with a price matrix, and sampling
        the dataset using the indices that belong to the same cluster.

        Parameters
        ----------
        indices: iterable with indices of symbols of interest.

        Returns
        -------
        A new EquityEOD object with just those symbols.
        """

        sample_symbols = set()
        for index in indices:
            sample_symbols.add(self.index_to_symbols[index])

        sample_listings = list(
            filter(lambda listing: listing.symbol in sample_symbols, self.listings)
        )

        sample_dataframes = dict()
        for symbol in sample_symbols:
            sample_dataframes[symbol] = self.data_frames[symbol]

        return DailyBar(
            sample_listings, sample_dataframes, self.start_date, self.end_date
        )
