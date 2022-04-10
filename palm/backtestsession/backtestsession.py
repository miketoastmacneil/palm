from datetime import datetime, timedelta

from palm.data.equity_eod import EquityEOD

from ..context import ContextEOD, EODEvent
from ..data import pull_polygon_eod
from ..trader import SimulatedTrader


class Strategy:
    def init_context(self) -> ContextEOD:
        pass

    def on_update(self, historical_data, context, trader):
        pass


class BacktestSession:
    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        look_back_period: timedelta,
        initial_capital=10000.0,
        symbols=None,
        dataset: EquityEOD = None,
    ):

        if (symbols is None) and (dataset is None):
            RuntimeError(
                """
                Backtest session requires either a set of symbols to 
                pull, or a dataset to iterate over. Got:
                    Symbols: {},
                    Dataset: {}
            """.format(
                    symbols, dataset
                )
            )

        self._symbols = symbols if symbols is not None else dataset.symbols
        self._start_date = start_date
        self._end_date = end_date
        self._look_back = look_back_period
        self._initial_capital = initial_capital
        self._strategies: list[Strategy] = []

        self._historical_data = (
            dataset
            if dataset is not None
            else pull_polygon_eod(symbols, start_date - look_back_period, end_date)
        )
        self._context = ContextEOD(self._historical_data, start_date)
        self._trader = SimulatedTrader(self._context, self._initial_capital)

    @property
    def cash_account(self):
        return self._trader.broker.cash_account

    @property
    def historical_data(self):
        return self._historical_data.slice(
            self._start_date - self._look_back, self._context.current_date()
        )

    @property
    def trader(self):
        return self._trader

    def add_strategy(self, strategy):
        self._strategies.append(strategy)

    def events(self):
        return self._context.__iter__()

    def run(self):

        if len(self._strategies) == 0:
            raise RuntimeError("Need at least one strategy to run a backtest.")

        self.portfolio_history = []

        for time_event in self.events():  ## trader will react to updates
            windowed_historical_data = self.historical_data
            for strategy in self._strategies:
                has_time_filters = hasattr(strategy, "time_filters")
                keep_time_event = True
                if has_time_filters:
                    for filter in strategy.time_filters:
                        keep_time_event = keep_time_event and filter(time_event)
                if keep_time_event:
                    strategy.on_update(
                        windowed_historical_data, self._context, self._trader
                    )
                else:
                    continue

            self.portfolio_history.append(self._trader.broker.portfolio_value())
