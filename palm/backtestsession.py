from abc import abstractmethod
from pandas.tseries.offsets import BDay
import pandas as pd
from typing import List

from .daily_bar_context import EODEvent, TimeInMarketDay, ContextEOD
from .equity_eod import EquityEOD
from .trader import SimulatedTrader

class Strategy:
    def __init__(self) -> None:
        self.look_back = 0

    @abstractmethod
    def on_update(self, historical_data: EquityEOD, context: ContextEOD, trader: SimulatedTrader) -> None:
        pass

    def trade_on_this_event(self, time_event: EODEvent) -> bool:
        if time_event.date_index_since_start < self.look_back:
            return False
        elif not hasattr(self, "time_filters"):
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


class Backtest:
    def __init__(
        self,
        strategy: Strategy,
        eod_data: EquityEOD,
        initial_capital=10000.0,
    ):
        self._initial_capital = initial_capital
        self._strategy: Strategy = strategy
        self._historical_data = eod_data

        self._context = ContextEOD(eod_data)
        self._trader = SimulatedTrader(self._context, initial_capital)

        self._has_run = False
        self._symbols = eod_data.symbols ## Used in results collection

    def run(self):

        if self._has_run:
            raise RuntimeError("Backtest already run, exiting.")

        results = []

        for time_event in self._context:
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

        return self._results_to_dataframe(results)

    def _results_to_dataframe(self, results: List[SimulatedTrader.Snapshot]):
        
        ## Positions
        dict_of_results = {}
        dict_of_results["Cash"] = []
        dict_of_results["Portfolio Value"] = []
        for symbol in self._symbols:
            dict_of_results[symbol] = []

        for result in results:
            dict_of_results["cash"].append(result.cash_balance)
            for symbol in self._symbols:
                if symbol in result.positions.keys():
                    dict_of_results[symbol].append(result.positions[symbol])
                else:
                    dict_of_results[symbol].append(0.0)
                
            dict_of_results["Portfolio Value"].append(result.portfolio_value)

        return pd.DataFrame(dict_of_results)

        

                

