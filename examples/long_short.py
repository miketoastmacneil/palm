
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

import palm as pm

start_date = datetime(2019, 5, 1)
end_date = datetime(2020, 10, 1)

symbol_list = ['AAPL', 'MSFT']
closing_prices = data.close_prices()
historical_portfolio_value = []

is_close = lambda time_event: time_event.time_in_market_day == pm.TimeInMarketDay.Closing
    
backtest = pm.BacktestSession(symbol_list, start_date, end_date, look_back)

for time_event in filter(lambda event: palm.is_close(event), backtest.events()):
    ## Same code here. That should be all thats needed.
    backtest.trader.liqudate_all_positions()

    t = time_event.data_index_since_start

    returns_since_yesterday = (closing_prices[t,:]- closing_prices[t-1,:]) / closing_prices[t-1, :]
    percent_returns = returns_since_yesterday/np.sum(np.abs(returns_since_yesterday))
    median_return = np.median(percent_returns)

    order_quantity = dict()
    for i in range(len(returns_since_yesterday)):
        amount_to_invest = -(percent_returns[i]) * back_test.trader.cash_balance
        order_quantity[symbol_list[i]] = int(round(amount_to_invest / context.current_market_price(symbol_list[i])))

    backtest.trader.submit_trade(order_quantity)

plt.plot(backtest.portfolio_value())
plt.plot(backtest.historical_data.close_prices())
plt.show()