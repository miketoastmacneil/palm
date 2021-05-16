
from enum import Enum
import pprint
from typing import Callable, Dict

from ..data.equity_eod import EquityEOD

class ContextEOD:
    """
    Context object used in Simulation. 

    Has two functions. To iterate over the historical 
    dataset for backtesting, and to be an observable so
    that assets can update their price.
    """

    class TimeInMarketDay(Enum):
        Opening = 1
        Closing = 2 

    def __init__(self, data_source: EquityEOD):
        self._data_source        = data_source
        self._current_date_index = 0
        self._time_in_market_day = ContextEOD.TimeInMarketDay.Opening

        self._open  = self._data_source.open_prices_array()
        self._close = self._data_source.close_prices_array() 
        self._dates = self._data_source.dates()

        T, _ = data_source.shape
        self._max_date_index = T-1
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

    def can_still_update(self):
        """
        "end" of the iterator
        """
        at_the_last_day = self._current_date_index == self._max_date_index
        at_closing_time = self._time_in_market_day == ContextEOD.TimeInMarketDay.Closing 

        its_closing_time_on_the_last_day = at_closing_time and at_the_last_day

        if its_closing_time_on_the_last_day:
            return False
        else:
            return True

    def update(self):
        """
        'next' for the iterator
        """
        if not self.can_still_update():
            return
        
        if self._time_in_market_day == ContextEOD.TimeInMarketDay.Opening:
            self._time_in_market_day = ContextEOD.TimeInMarketDay.Closing
        else:
            self._time_in_market_day = ContextEOD.TimeInMarketDay.Opening
            self._current_date_index = self._current_date_index + 1
        
        self.notify_observers()

    def notify_observers(self):
        for id in self._observers.keys():
            self._observers[id]()

    def time_in_market_day(self):
        return self._time_in_market_day

    def current_date_index(self):
        return self._current_date_index

    def current_date(self):
        return self._dates[self._current_date_index]


    ## TODO, this needs to give the right time
    def current_time(self):
        return self.current_date()

    def current_market_price(self, symbol):
        """
        This is what most of the observables are monitoring.
        Its not needed for the alpha model but this is
        how each price is updated.
        """
        t = self._current_date_index
        i = self._data_source.symbol_to_column_index[symbol]
        if self._time_in_market_day == ContextEOD.TimeInMarketDay.Opening:
            return self._open[t, i]
        elif self._time_in_market_day == ContextEOD.TimeInMarketDay.Closing:
            return self._close[t, i]

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent = 4)
        state = {
            "Time In Market Day": "Opening" if self._time_in_market_day==ContextEOD.TimeInMarketDay.Opening else "Closing",
            "Current Time Index": self._current_date_index,
            "Current Date in Simulation": self.current_date().date()
        }
        return pp.pformat(state)