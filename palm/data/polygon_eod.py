
import os
from functools import lru_cache
from palm.data.equity_eod import EquityEOD
from pprint import PrettyPrinter
import pytz
from typing import List
import os

from datetime import datetime
import numpy as np
import pandas as pd 
from pandas.tseries.offsets import BDay

from .data_utils import *

class PolygonEOD(EquityEOD):
    """
    Implements the Equity EOD interface for Polygon IO data.
    """

    def __init__(self, data: dict):
        self.data = data
        self.symbols = sorted(set(self.data.keys()))
        self._dates = data[self.symbols[0]].index
        
        self._index_to_symbol = {}
        self._symbol_to_index = {}
        for (index, symbol) in enumerate(self.symbols):
            self._index_to_symbol[index] = symbol
            self._symbol_to_index[symbol] = index

        self.start_date  = self._dates[0]
        self.end_date    = self._dates[-1]

        self.shape = (len(self._dates), len(self.symbols))

        return        

    @property
    def column_index_to_symbol(self):
        return self._index_to_symbol

    @property
    def symbol_to_column_index(self):
        return self._symbol_to_index

    def close_prices(self):
        return self._get_field_array('c')

    def open_prices(self):
        return self._get_field_array('o')

    def volume(self):
        return self._get_field_array('v')
    
    def high_prices(self):
        return self._get_field_array('h')

    def low_prices(self):
        return self._get_field_array('l')

    def dates(self):
        return self._dates

    @lru_cache(maxsize = 6)
    def _get_field_array(self, field_name):
        T,N = self.shape

        out = np.zeros((T,N))
        
        for (index, symbol) in enumerate(self.symbols):
            out[:, index] = self.data[symbol][field_name].to_numpy()

        return out
