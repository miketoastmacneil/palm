
from datetime import datetime
from palm.trades.trade import Trade
from palm.context.daily_bar_context import ContextEOD

import matplotlib.pyplot as plt
import numpy as np
import pandas_datareader as pdr

import palm
from palm.broker.simulated_broker import SimulatedBroker
from palm.orders.market_order import MarketOrder

start_date = datetime(2019, 1, 1)
end_date = datetime(2020, 10, 10)

symbol_list = ['BAC', 'BK', 'C', 'CFG',
                'CMA', 'COF', 'FITB', 'GS',
                'JPM', 'KEY', 'MS',
                'MTB', 'PBCT', 'PNC', 
                'STT', 'USB', 'WFC', 'ZION']

data = pdr.data.DataReader(symbol_list, 'yahoo', start_date, end_date)

context = palm.ContextFromYahooEOD(data)  ## TODO add "closing only "
broker = SimulatedBroker(context, initial_deposit= 10000)
account = broker.get_cast_account()

closing_prices = data["Close"].to_numpy()
historical_portfolio_value = []

while context.can_still_update():
    context.update()

    ## Skip openings
    if context.time_in_market_day() == context.TimeInMarketDay.Opening:
        continue

    t = context.current_date_index()
    returns_since_yesterday = (closing_prices[t,:]- closing_prices[t-1,:]) / closing_prices[t, :]
    percent_returns = returns_since_yesterday/np.sum(np.abs(returns_since_yesterday))
    median_return = np.median(percent_returns)

    order_quantity = dict()
    for i in range(len(returns_since_yesterday)):
        amount_to_invest = -(percent_returns[i] - median_return) * account.balance
        order_quantity[symbol_list[i]] = round(amount_to_invest / context.current_market_price(symbol_list[i]))

    ## Exit at next closing    
    exit_rule = lambda : context.current_date_index()==t+1 and context.time_in_market_day() == context.TimeInMarketDay.Closing

    trade = Trade(order_quantity, exit_rule)
    broker.submit_trade(trade)
    
    historical_portfolio_value.append(broker.portfolio_value())

plt.plot(historical_portfolio_value)
plt.show()