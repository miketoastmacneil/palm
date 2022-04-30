from datetime import datetime, timedelta
from functools import reduce
from re import S
import string

from pyparsing import stringStart

from palm.data.equity_eod import EquityEOD

from ..context import ContextEOD, EODEvent
from ..data import pull_polygon_eod
from ..trader import SimulatedTrader


class Strategy:

    def on_update(self, historical_data, context, trader):
        pass

    def user_set_symbols_correctly(self):
        has_symbols = hasattr(self, "symbols")
        if not has_symbols:
            return (False, """
                            Strategy doesn't have symbols it trades.
                            """)
        
        if type(self.symbols) != list:
            return (False, """ 
                            Strategy needs to provide a list
                            of symbols (i.e. ["SPY", "VXX"], or if there is only
                            one ["SPY"]), have: {}
                            """.format(self.symbols))

        all_elements_are_strings = reduce(lambda current_bool, element: current_bool and type(element) == str, True)
        if not all_elements_are_strings:
            return (False, """
                        All symbols in strategy need sa string, received: {}
                        """.format(self.symbols)
                )

        if len(self.symbols) == 0:
            return (False, """
                Provided strategy needs at least one symbol, got: {}
                """.format(self.symbols))

        return True


class BacktestSessionSubscribe:

    def __init__(
        self,
        strategy: Strategy,
        start_date: datetime,
        end_date: datetime,
        look_back_period: timedelta,
        initial_capital=10000.0,
    ):
        ## Check the strategy first.
        valid, failure_reason = self._validate_strategy(strategy)
        if not valid:
            raise RuntimeError(failure_reason) 

        self._start_date = start_date
        self._end_date = end_date
        if end_date <= start_date:
            raise ValueError("""
                End date cannot occur before start date. 
                Given start date: {}, Given end date: {}
            """.format(start_date, end_date))
        self._look_back = look_back_period
        self._initial_capital = initial_capital
        self._strategy: Strategy = strategy

        self._symbols = strategy.symbols()
        self._historical_data = pull_polygon_eod(self._symbols, start_date - look_back_period, end_date)
        
        ## Context doesn't need the end_date, that is already in historical
        ## data.
        self._context = ContextEOD(self._historical_data, start_date)
        self._trader = SimulatedTrader(self._context, initial_capital)
    
        self._has_run = False

    def run(self):
        
        if self._has_run:
            raise RuntimeError("Backtest already run, exiting.")
        
        self.results = []

        for time_event in self.events():
            windowed_historical_data = self._historical_data.slice(
                self._start_date - self._look_back, self._context.current_date()
            )
            if self._strategy.trade_on_this_time_event(time_event):
                self._strategy.on_update(
                    windowed_historical_data, self._context, self._trader
                )
            
        self._has_run = True

    def _validate_strategy(self, strategy):
        symbols = strategy.symbols()

    def _symbols_from_strategy(self, strategy):

        has_symbols = hasattr(strategy, "symbols")
        if not has_symbols:
            raise RuntimeError("""
                                Provided strategy doesn't have symbols it trades.
                                """)
        
        if type(strategy.symbols) == string:
            strategy.symbols = [strategy.symbols]
        
        if type(strategy.symbols) != list:
            raise RuntimeError(""" 
                                Provided Strategy needs to provide a list
                                of symbols, have: {}
                                """.format(strategy.symbols))

        if len(strategy.symbols) == 0:
            raise RuntimeError("Provided strategy needs at least one symbol".format(strategy.symbols))

        return strategy.symbols

    def _filter_time_event(self, strategy, time_event):
        return

    def _events(self):
        self._context.__iter__()
        return

    def _sliced_historical_data(self):
        return self._historical_data.slice(
            self._start_date - self._look_back, self._context.current_date()
        )