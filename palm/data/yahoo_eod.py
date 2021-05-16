

import pandas as pd

from .equity_eod import EquityEOD

class YahooEOD(EquityEOD):

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.symbols = list(data['Close'].columns)
        self._dates = data.index

        ## TODO, maybe just put this stuff into a get price method
        self._column_index_to_symbol = {}
        self._symbol_to_column_index = {}
        for (index, symbol) in enumerate(self.symbols):
            self._column_index_to_symbol[index] = symbol
            self._symbol_to_column_index[symbol] = index

        self.start_date  = self._dates[0]
        self.end_date    = self._dates[-1]

        self.shape = (len(self._dates), len(self.symbols))

        return        

    def close_prices_array(self):
        return self.data['Close'].to_numpy()     

    def open_prices_array(self):
        return self.data['Open'].to_numpy()     

    def dates(self):
        return self._dates

    @property
    def column_index_to_symbol(self):
        return self._column_index_to_symbol

    @property
    def symbol_to_column_index(self):
        return self._symbol_to_column_index
