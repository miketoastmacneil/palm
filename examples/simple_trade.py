
import pandas as pd

import os

from palm.data import PolygonEOD
from palm.context import ContextEOD, TimeInMarketDay
from palm.trader import SimulatedTrader, Trade

root_dir = "/Users/mikemacneil/Documents/github/palm/examples"

data = {}
data["AAPL"] = pd.read_csv(os.path.join(root_dir,"sample_data/AAPL-Sample-Data.csv"), index_col=0)
data["MSFT"] = pd.read_csv(os.path.join(root_dir,"sample_data/MSFT-Sample-Data.csv"), index_col=0)

eod_data = PolygonEOD(data)
context = ContextEOD(eod_data) 


initial_deposit = 10000
trader = SimulatedTrader(context, initial_deposit)

class ExitRule:

    def __init__(self, context, time_to_close):
        self.context = context
        self.time_to_close = time_to_close

    def __call__(self):
        is_closing = self.context.time_in_market_day()==TimeInMarketDay.Closing
        is_next_day = self.context.current_date_index()==self.time_to_close
        return (is_closing and is_next_day)


exit_rule = ExitRule(context, 1)
trade = Trade({"AAPL":1,"MSFT":-1}, exit_rule)
trader.submit_trade(trade)

context.update()
context.update()
context.update()

assert trade.exit_rule_triggered()
assert trade.status == Trade.Status.COMPLETE
assert trader.broker.all_positions == {}