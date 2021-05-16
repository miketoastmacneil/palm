
from abc import ABC, abstractmethod, abstractproperty

class EquityEOD(ABC):
    """
    Interface for Equity EOD giving the minimum amount of information
    needed for EOD Context.
    """

    @abstractmethod
    def close_prices_array(self): 
        pass

    @abstractmethod
    def open_prices_array(self):
        pass

    @abstractmethod
    def dates(self):
        pass

    @abstractproperty
    def symbol_to_column_index(self, symbol):
        pass