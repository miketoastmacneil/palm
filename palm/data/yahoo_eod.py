

import pandas as pd

from .equity_eod import EquityEOD

class YahooEOD(EquityEOD):
    """
    Class implementing the EquityEOD interface
    for Yahoo EOD data pulled from pandas_datareader.
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.symbols = list(data['Close'].columns)
        self._dates = data.index

        self._column_index_to_symbol = {}
        self._symbol_to_column_index = {}
        for (index, symbol) in enumerate(self.symbols):
            self._column_index_to_symbol[index] = symbol
            self._symbol_to_column_index[symbol] = index

        self.start_date  = self._dates[0]
        self.end_date    = self._dates[-1]

        self.shape = (len(self._dates), len(self.symbols))

        return        

    def close_prices(self):
        return self.data['Close'].to_numpy()     

    def open_prices(self):
        return self.data['Open'].to_numpy()     

    def dates(self):
        return self._dates

    def low_prices(self):
        return self.data['Low'].to_numpy()
    
    def high_prices(self):
        return self.data['High'].to_numpy()

    def volume(self):
        return self.data['Volume'].to_numpy()

    @property
    def column_index_to_symbol(self):
        return self._column_index_to_symbol

    @property
    def symbol_to_column_index(self):
        return self._symbol_to_column_index
