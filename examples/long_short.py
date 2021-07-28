
from datetime import datetime
from palm.data.data_utils import pull_polygon_eod
from palm.trades.trade import Trade
from palm.context.daily_bar_context import ContextEOD, TimeInMarketDay

import matplotlib.pyplot as plt
import numpy as np

import palm
from palm.broker.simulated_broker import SimulatedBroker
from palm.trader.trader import SimulatedTrader
from palm.orders.market_order import MarketOrder

start_date = datetime(2019, 1, 1)
end_date = datetime(2020, 10, 10)

symbol_list = ['BAC',  'C', 
                 'MS', 
                'JPM', 'GS']

data = pull_polygon_eod(symbol_list, start_date, end_date)

context = ContextEOD(data)
## Then do for event in context:
trader = SimulatedTrader(context, initial_deposit = 10000) ## This would also have the broker
broker = trader.broker
account = trader.broker.get_cast_account()

closing_prices = data.close_prices()
historical_portfolio_value = []

is_open = lambda time_event: time_event.time_in_market_day == TimeInMarketDay.Opening

class ExitRule:

    def __init__(self, context, time_to_close):
        self.context = context
        self.time_to_close = time_to_close

    def __call__(self):
        is_closing = self.context.time_in_market_day()==TimeInMarketDay.Closing
        is_next_day = self.context.current_date_index()==self.time_to_close
        return (is_closing and is_next_day)

for time_event in context:

    ## Skip openings
    if is_open(time_event):
        continue

    t = time_event.date_index_since_start
    returns_since_yesterday = (closing_prices[t,:]- closing_prices[t-1,:]) / closing_prices[t, :]
    percent_returns = returns_since_yesterday/np.sum(np.abs(returns_since_yesterday))
    median_return = np.median(percent_returns)

    order_quantity = dict()
    for i in range(len(returns_since_yesterday)):
        amount_to_invest = -(percent_returns[i] - median_return) * account.balance
        order_quantity[symbol_list[i]] = round(amount_to_invest / context.current_market_price(symbol_list[i]))

    ## Exit at next closing    
    exit_rule = ExitRule(context, t+4)

    trade = Trade(order_quantity, exit_rule)
    trader.submit_trade(trade)
    
    historical_portfolio_value.append(broker.portfolio_value())

plt.plot(historical_portfolio_value)
plt.show()