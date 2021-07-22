
from abc import ABC, abstractmethod, abstractproperty

class EquityEOD(ABC):
    """
    Interface for Equity EOD giving the minimum amount of information
    needed for EOD Context. 

    The main assumption is that EOD data can be written
    in the form of several TxN matrices, where T is the number
    of dates and N is the number of assets.
    """

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