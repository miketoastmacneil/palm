from datetime import date
import pandas as pd

equity_eod_fields = ["open", "close", "high", "low", "volume"]

class EquityEOD:
    """
    EOD data is given as a collection of TxN matrices, one for each field:
    "open", "close", "high", "low", "volume".
    """

    def __init__(self, data):

        if not (set(equity_eod_fields).issubset(set(data.keys()))):
            raise ValueError(
                "Data must be a dictionary of data frames with the fields: {}".format(
                    equity_eod_fields
                )
            )

        self._data = data
        self.symbols = self._data["open"].columns
        for field in equity_eod_fields:
            self._data[field].index = pd.to_datetime(self._data[field].index).date
        self._dates = pd.to_datetime(self._data["open"].index).date

        self._index_to_symbol = {}
        self._symbol_to_index = {}
        for (index, symbol) in enumerate(self.symbols):
            self._index_to_symbol[index] = symbol
            self._symbol_to_index[symbol] = index

        self.start_date = self._dates[0]
        self.end_date = self._dates[-1]

        self.shape = (len(self._dates), len(self.symbols))

        return

    @property
    def dates(self):
        return self._dates

    @property
    def open(self):
        return self._data["open"]

    @property
    def close(self):
        return self._data["close"]

    @property
    def high(self):
        return self._data["high"]

    @property
    def low(self):
        return self._data["low"]

    @property
    def volume(self):
        return self._data["volume"]

    def __getitem__(self, key: str):
        if type(key) != str:
            raise ValueError("Data needs a string key")

        return self._data[key]

    def __len__(self):
        T, _ = self.shape
        return T

    def slice(self, from_date: date, to_date: date):
        """
        Slices the data set from a start date up to,
        but not including, and end date.
        """
        if from_date>=to_date:
            return None

        sliced_data = {}
        for field in self._data.keys():
            data_at_field = self._data[field]
            sliced_data[field] = data_at_field[data_at_field.index >= from_date]
            sliced_data[field] = sliced_data[field][sliced_data[field].index < to_date]

        return EquityEOD(sliced_data)

    def slice_by_indices(self, from_idx: int, to_idx: int):
        return
