from datetime import datetime
from enum import Enum
import numpy as np
import pprint

from ..data import EquityEOD
from .context_observable import ContextObservable


class TimeInMarketDay(Enum):
    Open = 1
    Close = 2

class EODEvent:
    """
    End of Day time events for simulation, provides the
    use with what date it is and whether it is opening or closing.
    In backtesting "date_index_since_start" is provided for convenience.
    """

    def __init__(self, date, time_in_market_day, date_index_since_start):

        self.date = date
        self.time_in_market_day = time_in_market_day
        self.date_index_since_start = date_index_since_start

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent=4)
        state = {
            "Time In Market Day": "Opening"
            if self.time_in_market_day == TimeInMarketDay.Open
            else "Closing",
            "Date Index Since Start": self.date_index_since_start,
            "Date": self.date,
        }
        return pp.pformat(state)


class ContextEOD(ContextObservable):
    """
    Object used to generate events for
    a historical dataset as well as being
    the single source of truth for current and
    previous price information.

    Iterator Example:
    -----------------
    from datetime import datetime
    from palm.data.data_utils import pull_data_from_polygon
    from palm.context.daily_bar_context import ContextEOD

    symbols = ['MSFT']
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2019, 2, 1)

    data = pull_data_from_polygon(symbols, start_date, end_date)
    context = ContextEOD(data)

    for time_event in context:
        print(time_event) ## EOD time event from above.
        print(context) ## will update for each event generated

    Subscribable Example:
    ---------------------
    from datetime import datetime
    from palm.data.data_utils import pull_data_from_polygon
    from palm.context.daily_bar_context import ContextEOD

    import rx

    symbols = ['MSFT']
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2019, 2, 1)

    data = pull_data_from_polygon(symbols, start_date, end_date)
    context = ContextEOD(data)

    observable = rx.from_iterable(context)
    observable.subscribe(lambda time_event: print(time_event))
    """

    def __init__(
        self,
        data_source: EquityEOD,
        start_index: int = 0
    ):
        super(ContextEOD, self).__init__()
        self._data = data_source

        self._open = self._data["open"].to_numpy()
        self._close = self._data["close"].to_numpy()
        self._dates = self._data.dates

        self._start_date_index = start_index
        self._current_date_index = self._start_date_index
        self._time_in_market_day = TimeInMarketDay.Open

        T, _ = data_source.shape
        self._max_date_index = T - 1

        self._iterator_needs_to_update = False

    def current_market_price(self, symbol):
        t = self._current_date_index
        i = self._data.symbol_to_column_index[symbol]
        if self._time_in_market_day == TimeInMarketDay.Open:
            return self._open[t, i]
        elif self._time_in_market_day == TimeInMarketDay.Close:
            return self._close[t, i]

    def current_market_prices(self):

        t = self._current_date_index
        if self._time_in_market_day == TimeInMarketDay.Open:
            return self._open[t, :]
        elif self._time_in_market_day == TimeInMarketDay.Close:
            return self._close[t, :]

    def time_in_market_day(self):
        return self._time_in_market_day

    def date_index_since_start(self):
        return self._current_date_index - self._start_date_index

    def current_date_index(self):
        return self._current_date_index

    def current_date(self):
        return self._dates[self._current_date_index]

    @property
    def historical_data(self):
        return self._historical_data

    ## TODO, this needs to give the right time
    ## To confirm when orders are submitted
    def current_time(self):
        return self.current_date()

    def update(self):
        """
        'next' for the iterator
        """
        if not self.can_still_update():
            return

        if self._time_in_market_day == TimeInMarketDay.Open:
            self._time_in_market_day = TimeInMarketDay.Close
        else:
            self._time_in_market_day = TimeInMarketDay.Open
            self._current_date_index = self._current_date_index + 1

        self.notify_observers()

    def can_still_update(self):
        """
        "end" of the iterator
        """
        at_the_last_day = self._current_date_index == self._max_date_index
        at_closing_time = self._time_in_market_day == TimeInMarketDay.Close

        its_closing_time_on_the_last_day = at_closing_time and at_the_last_day

        if its_closing_time_on_the_last_day:
            return False
        else:
            return True

    def __iter__(self):

        while self.can_still_update():
            ## Update myself before sending the event.
            event = None
            if not self._iterator_needs_to_update:
                event = EODEvent(
                    self._dates[self.current_date_index()],
                    self._time_in_market_day,
                    self.current_date_index(),
                )
                self._iterator_needs_to_update = True
            else:
                self.update()
                event = EODEvent(
                    self._dates[self.current_date_index()],
                    self._time_in_market_day,
                    self.current_date_index(),
                )
            yield event

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent=4)
        state = {
            "Time In Market Day": "Opening"
            if self._time_in_market_day == TimeInMarketDay.Open
            else "Closing",
            "Current Time Index": self._current_date_index,
            "Current Date in Simulation": self.current_date(),
        }
        return pp.pformat(state)
