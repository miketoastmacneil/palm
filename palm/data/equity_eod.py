from datetime import datetime
import numpy as np
import pandas as pd

equity_eod_fields = ["open", "close", "high", "low", "volume"]


class EquityEOD:
    """
    EOD data is given as a collection of TxN matrices, one for each field:
    "Open", "Close", "High", "Low", "Volume".
    """

    def __init__(self, data):
        self._allowed_fields = equity_eod_fields
        self._allowed_return_types = ["numpy", "dataframe"]
        self._return_type = "numpy"

        if not (self._allowed_fields == list(data.keys())):
            raise ValueError(
                "Data must be a dictionary of data frames with the fields: {}".format(
                    self._allowed_fields
                )
            )

        ## Add a validate dataset here.
        self._data = data
        self.symbols = sorted(set(self._data["open"].columns))
        self._dates = pd.to_datetime(self._data["open"].index)

        self._index_to_symbol = {}
        self._symbol_to_index = {}
        for (index, symbol) in enumerate(self.symbols):
            self._index_to_symbol[index] = symbol
            self._symbol_to_index[symbol] = index

        self.start_date = self._dates[0]
        self.end_date = self._dates[-1]

        self.shape = (len(self._dates), len(self.symbols))

        return

    def __getitem__(self, key: str):
        if type(key) != str:
            raise ValueError("Data needs a string key")

        if key == "dates":
            return self._dates

        if key not in self._allowed_fields:
            raise ValueError(
                "Key: {},  not recognized. Accepted values are: {}".format(
                    key, self._allowed_fields
                )
            )

        if self.return_type == "numpy":
            return self._data[key].to_numpy()
        elif self.return_type == "dataframe":
            return self._data[key]
        else:
            return

    @property
    def return_type(self):
        return self._return_type

    @return_type.setter
    def return_type(self, new_value):
        if new_value not in self._allowed_return_types:
            raise ValueError(
                f""" 
                Return type must be one of {self._allowed_return_types}, 
                received {new_value}.
            """
            )
        else:
            self._return_type = new_value

    def slice(self, from_date: datetime, to_date: datetime):
        """
        Slices the data set from a start date up to,
        but not including, and end date.
        """

        sliced_data = {}
        for field in self._allowed_fields:
            data_at_field = self._data[field]
            sliced_data[field] = data_at_field[data_at_field.index >= from_date]
            sliced_data[field] = sliced_data[field][sliced_data[field].index < to_date]

        return EquityEOD(sliced_data)

    @property
    def column_index_to_symbol(self):
        return self._index_to_symbol

    @property
    def symbol_to_column_index(self):
        return self._symbol_to_index
