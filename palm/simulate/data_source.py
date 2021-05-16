
from abc import ABCMeta, abstractmethod
from typing import List, Tuple
import numpy as np

from .universe import EquityUniverse

class DataSource(metaclass = ABCMeta):
    """
    Defines the interface for a Data Source which
    can be used for running back tests. It needs 
    to be able to provide

    - returns.
    - prices.
    - shape in the form of (T, N). T is the maximum time index,
        N is the number of assets.
    - index_to_symbol_dict: a dictionary providing
        a way to convert between an assets index in the datasource
        and its ticker symbol
    - universe: a 
    """
    
    @abstractmethod
    def prices(self, symbol: str, time_index: int) -> float:
        pass

    @property
    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        pass

    @property
    @abstractmethod
    def universe(self) -> EquityUniverse:
        pass
