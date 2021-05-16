
from enum import Enum
import pprint
from typing import Callable, Dict

from ..data.daily_bar import EquityEOD

class ContextEOD:
    """
    Context object used in Simulation. 

    Has two functions. To iterate over the historical 
    dataset for backtesting, and to be an observable so
    that assets can keep a record of their
    price history.
    """

    class TimeInMarketDay(Enum):
        Opening = 1
        Closing = 2 

    def __init__(self, data_source: EquityEOD):
        self._data_source        = data_source
        self._current_time_index = 0
        self._time_in_market_day = ContextEOD.TimeInMarketDay.Opening

        self._open  = self._data_source.open_prices()
        self._close = self._data_source.close_prices() 

        T, _ = data_source.shape
        self._max_time = T-1

        self._observers: Dict[str, Callable] = dict()

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

    def step(self):
        if self._time_in_market_day == ContextEOD.TimeInMarketDay.Opening:
            self._time_in_market_day = ContextEOD.TimeInMarketDay.Closing
        else:
            self._time_in_market_day = ContextEOD.TimeInMarketDay.Opening
            self.current_time_index = self.current_time_index+1
        
        self.notify_observers()

        return

    def notify_observers(self):
        for id in self._observers.keys():
            self._observers[id]()

    @property
    def symbols(self):
        return set(self._data_source.symbols)

    @property
    def time_in_market_day(self):
        return self._time_in_market_day

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

    def current_market_price(self, symbol):
        """
        This is what most of the observables are monitoring.
        Its not needed for the alpha model but this is
        how each price is updated.
        """
        t = self.current_time_index
        i = self._data_source.symbol_to_index[symbol]
        if self.time_in_market_day==ContextEOD.TimeInMarketDay.Opening:
            return self._open[t, i]
        elif self.time_in_market_day==ContextEOD.TimeInMarketDay.Closing:
            return self._close[t,i]

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent = 4)
        state = {
            "Time In Market Day": "Opening" if self.time_in_market_day==ContextEOD.TimeInMarketDay.Opening else "Closing",
            "Current Time Index": self.current_time_index,
            "Current Date in Simulation": self._data_source.time_stamps[self.current_time_index]
        }
        return pp.pformat(state)