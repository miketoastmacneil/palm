from datetime import datetime
from palm.data.data_utils import pull_polygon_eod
from palm.context.daily_bar_context import ContextEOD, TimeInMarketDay

import matplotlib.pyplot as plt
import numpy as np
import pandas_datareader as pdr

import palm
from palm.trader.trader import SimulatedTrader
from palm.trades.trade import Trade

start_date = datetime(2019, 1, 1)
end_date = datetime(2020, 10, 10)

symbol_list = ["AAPL"]

data = pull_polygon_eod(symbol_list, start_date, end_date)

context = ContextEOD(data)
trader = SimulatedTrader(context, initial_deposit=10000)

account = trader.broker.get_cast_account()

closing_prices = data.close_prices()
portfolio_value_history = []

is_open = lambda time_event: time_event.time_in_market_day == TimeInMarketDay.Opening
less_than_30_days_data = lambda time_event: time_event.time_index_since_start < 15

for time_event in context:
    if is_open(time_event) or less_than_30_days_data(time_event):
        continue

    t = time_event.time_index_since_start

    ## Ranges in numpy cut off the last one
    previous_30_day_close = closing_prices[t - 10 : t + 1]

    aapl_current_price = context.current_market_price("AAPL")
    aapl_previous_n_days = np.mean(previous_30_day_close)

    ## Lambdas in python don't capture local scope.
    def exit_rule():
        stop_loss = 1.05 * aapl_current_price
        context.current_market_price("AAPL") > stop_loss
        return context.current_date_index() == t + 1

    if aapl_current_price > aapl_previous_n_days:
        trader.submit_trade(Trade({"AAPL": -1}, exit_rule))

    portfolio_value_history.append(trader.broker.portfolio_value())

plt.plot(portfolio_value_history)
plt.show()
