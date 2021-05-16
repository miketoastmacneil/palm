
from .universe import EquityUniverse
from typing import Callable, Dict

from .data_source import DataSource

class Context:
    """
    Context object used in Simulation. 

    Its an Observable, and holds onto a private list of 
    Observables in the form of callbacks. Once the current
    time index is updated (making all datasources current),
    each observable can update their own state according to a 
    callback.
    """

    def __init__(self, universe: EquityUniverse, data_source: DataSource):
        self._data_source        = data_source
        self._current_time_index = 0

        T, _ = data_source.shape
        self._max_time = T-1

        self._observers: Dict[str,Callable] = []
        ## Have current_time_index to time

    def add_observer(self, id, callback: Callable):
        if id in self._observers.keys():
            return
        else:
            self._observers[id] = callback

    def remove_observer(self, id):
        if id in self._observers.keys():
            del self._observers[id]
        else:
            return

    @property
    def current_time_index(self):
        return self._current_time_index

    @current_time_index.setter
    def current_time_index(self, value):
        if self._current_time_index==value:
            return
        if value>=self._max_time:
            raise RuntimeError("Index out of bounds for Contexts dataset.")
        else:
            self._current_time_index = value
            for id in self._observers.keys():
                self._observers[id]()

    def current_price(self, symbol):
        """
        Return the current prices for each asset.
        """
        return self._data_source.prices(symbol,self.current_time_index)


    def historical_data(self, look_back_period):
        """
        Returns a set of historical data t-look_back_period to current time.
        """

        return self._data_source.historical_data(self.current_time_index-look_back_period, self.current_time_index)
