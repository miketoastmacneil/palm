from datetime import datetime
from functools import reduce
from pandas.tseries.offsets import BDay

from palm.data.equity_eod import EquityEOD

from ..context import ContextEOD
from ..data import pull_polygon_eod
from ..trader import SimulatedTrader


class Strategy:
    def on_update(self, historical_data, context, trader):
        pass

    def user_set_symbols_correctly(self):
        has_symbols = hasattr(self, "symbols")
        if not has_symbols:
            return (
                False,
                """
                            Strategy doesn't have symbols it trades.
                            """,
            )

        if type(self.symbols) != list:
            return (
                False,
                """ 
                            Strategy needs to provide a list
                            of symbols (i.e. ["SPY", "VXX"], or if there is only
                            one ["SPY"]), have: {}
                            """.format(
                    self.symbols
                ),
            )

        if len(self.symbols) == 0:
            return (
                False,
                """
                Provided strategy needs at least one symbol, got: {}
                """.format(
                    self.symbols
                ),
            )

        all_elements_are_strings = reduce(
            lambda current_bool, element: current_bool and type(element) == str,
            self.symbols,
            True,
        )
        if not all_elements_are_strings:
            return (
                False,
                """
                        All symbols in strategy need sa string, received: {}
                        """.format(
                    self.symbols
                ),
            )

        return (True, "")


class BacktestSubscribeSession:

    def __init__(
        self,
        strategy: Strategy,
        eod_data: EquityEOD,
        look_back_days: int = 30,
        initial_capital=10000.0,
    ):
        ## Check the strategy first.
        valid, failure_reason = self._validate_strategy(strategy)
        if not valid:
            raise ValueError(failure_reason)

        self._initial_capital = initial_capital
        self._strategy: Strategy = strategy

        self._symbols = strategy.symbols

        historical_data_has_strategy_symbols, error_message = (
            self._strategy_symbols_contained_in_historical_data(
                self._symbols, eod_data 
            )
        )
        if historical_data_has_strategy_symbols:
            self._historical_data = eod_data
        else:
            raise ValueError(error_message)

        self._look_back_period = BDay(look_back_days)
        self._context = ContextEOD(self._historical_data, start_index = look_back_days)
        self._start_date = self._context.current_date()

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

    def _validate_strategy(self, strategy: Strategy):
        symbols_set_correctly, message = strategy.user_set_symbols_correctly()
        return symbols_set_correctly, message

    def _events(self):
        self._context.__iter__()
        return

    def _sliced_historical_data(self):
        return self._historical_data.slice(
            self._start_date - self._look_back, self._context.current_date()
        )
    def _strategy_symbols_contained_in_historical_data(self, symbols, data):

        data_symbols = set(data.symbols)
        all_contained = reduce(lambda current_bool, element: current_bool and (element in data_symbols), symbols, True)
        error_message = "" if all_contained else "Historical data doesn't contain all symbols needed for strategy."
        return (all_contained, error_message)

        
