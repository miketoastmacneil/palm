from abc import ABC, abstractmethod, abstractproperty


class EquityEOD(ABC):
    """
    Interface for Equity EOD giving the minimum amount of information
    needed for EOD Context.

    The main assumption is that EOD data can be written
    in the form of several TxN matrices, where T is the number
    of dates and N is the number of assets.
    """

    def __init__(self, data_dictionary, field_keys):

        return

    @abstractmethod
    def close_prices(self):
        pass

    @abstractmethod
    def open_prices(self):
        pass

    @abstractmethod
    def high_prices(self):
        pass

    @abstractmethod
    def low_prices(self):
        pass

    @abstractmethod
    def volume(self):
        pass

    @abstractmethod
    def dates(self):
        pass

    @abstractproperty
    def symbol_to_column_index(self):
        pass

    @abstractproperty
    def column_index_to_symbol(self):
        pass

    @lru_cache(maxsize=6)
    def _get_field_array(self, field_name):
        """
        Gets the T x N array for some specified field name.
        In the case that data isn't available for certain indices, the data is filled with NaN.
        """
        T, N = self.shape

        out = np.zeros((T, N))

        for (index, symbol) in enumerate(self.symbols):
            column = self.data[symbol][field_name].to_numpy()
            out[: len(column), index] = column

        return out
