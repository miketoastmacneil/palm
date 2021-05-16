from abc import ABCMeta, abstractmethod
from typing import List
import numpy as np

from ..asset.equity import PolygonEquity

class EquityUniverse(metaclass = ABCMeta):
    """
    Defines the interface for a universe of assets.
    Needs to provide 

    - A set of listings with the polygon equity class
    """

    @property
    @abstractmethod
    def listings(self) -> List[PolygonEquity]:
        pass
    
    @property
    @abstractmethod
    def symbols(self) -> List[str]:
        pass
