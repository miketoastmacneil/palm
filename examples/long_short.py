
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

import palm as pm

start_date = datetime(2019, 5, 1)
end_date = datetime(2020, 10, 1)

symbol_list = ['AAPL', 'MSFT']

data = pm.pull_polygon_eod(symbol_list, start_date, end_date)

context = pm.ContextEOD(data)
## Then do for event in context:
trader = pm.SimulatedTrader(context, initial_deposit = 10000) ## This would also have the broker
broker = trader.broker
account = trader.broker.cash_account

closing_prices = data.close_prices()
historical_portfolio_value = []

is_close = lambda time_event: time_event.time_in_market_day == pm.TimeInMarketDay.Closing

class ExitRule:

    def __init__(self, context, time_to_close):
        self.context = context
        self.time_to_close = time_to_close

    def __call__(self):
        is_closing = self.context.time_in_market_day()==pm.TimeInMarketDay.Closing
        is_next_day = self.context.current_date_index()==self.time_to_close
        return (is_closing and is_next_day)

for time_event in filter(lambda event: is_close(event), context):

    ## Skip openings
    t = time_event.date_index_since_start
    returns_since_yesterday = (closing_prices[t,:]- closing_prices[t-1,:]) / closing_prices[t-1, :]
    percent_returns = returns_since_yesterday/np.sum(np.abs(returns_since_yesterday))
    median_return = np.median(percent_returns)

    order_quantity = dict()
    for i in range(len(returns_since_yesterday)):
        amount_to_invest = -(percent_returns[i]) * account.balance
        order_quantity[symbol_list[i]] = int(round(amount_to_invest / context.current_market_price(symbol_list[i])))

    ## Exit at next closing    
    exit_rule = ExitRule(context, t+1)

    trade = pm.Trade(order_quantity, exit_rule)
    trader.submit_trade(trade)
    historical_portfolio_value.append(broker.portfolio_value())
    

plt.plot(np.array(historical_portfolio_value))
plt.plot(data.close_prices())
plt.show()