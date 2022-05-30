from functools import reduce
from pandas.tseries.offsets import BDay

from ..context.daily_bar_context import TimeInMarketDay

from ..data import EquityEOD
from ..context import ContextEOD
from ..trader import SimulatedTrader

class Strategy:
    def __init__(self) -> None:
        self.look_back = 0

    def on_update(self, historical_data, context, trader):
        pass

    def user_set_a_look_back(self):
        return

    ## If symbols are set by the dataset, why does it matter with the dataset?
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

    def trade_on_this_event(self, time_event):
        if not hasattr(self, "time_filters"):
            return True 
        else:
            keep_time_event = True
            for filter in self.time_filters:
                filtered = filter(time_event)
                if type(filtered) is not bool:
                    raise ValueError(
                        f"""Return value of time filter needs to be boolean. Got return value: {filtered},
                    from time filter:{filter}."""
                    )
                keep_time_event = keep_time_event and filter(time_event)
            return keep_time_event


class BacktestSubscribeSession:
    def __init__(
        self,
        strategy: Strategy,
        eod_data: EquityEOD,
        initial_capital=10000.0,
    ):
        self._initial_capital = initial_capital
        self._strategy: Strategy = strategy
        self._symbols = eod_data.symbols
        self._historical_data = eod_data

        self._context = ContextEOD(eod_data)
        self._trader = SimulatedTrader(self._context, initial_capital)

        self._has_run = False

    def run(self):

        if self._has_run:
            raise RuntimeError("Backtest already run, exiting.")

        results = []

        for time_event in filter(self._strategy.trade_on_this_event, self._context):
            if self._strategy.trade_on_this_event(time_event):    
                windowed_historical_data = None
                if time_event.date_index_since_start > 0:
                    windowed_historical_data = self._historical_data.slice(
                        time_event.date - BDay(self._strategy.look_back),
                        time_event.date,
                    )
                self._strategy.on_update(
                    windowed_historical_data, self._context, self._trader
                )
            ## Only update snapshot on close
            if time_event.time_in_market_day == TimeInMarketDay.Close:
                results.append(self._trader.state)

        self._has_run = True

        return results

    def _validate_strategy(self, strategy: Strategy):
        symbols_set_correctly, message = strategy.user_set_symbols_correctly()
        return symbols_set_correctly, message

    def _strategy_symbols_contained_in_historical_data(self, symbols, data):

        data_symbols = set(data.symbols)
        all_contained = reduce(
            lambda current_bool, element: current_bool and (element in data_symbols),
            symbols,
            True,
        )
        error_message = (
            ""
            if all_contained
            else "Historical data doesn't contain all symbols needed for strategy."
        )
        return (all_contained, error_message)
