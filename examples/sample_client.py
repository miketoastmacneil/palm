

from datetime import datetime
from palm.context.daily_bar_context import ContextEOD

import numpy as np
import pandas_datareader as pdr

import palm
from palm.broker.simulated_broker import SimulatedBroker
from palm.orders.market_order import MarketOrder

start_date = datetime(2019, 1, 1)
end_date = datetime(2020, 10, 10)

symbol_list = ['AAPL']

data = pdr.data.DataReader(symbol_list, 'yahoo', start_date, end_date)

context = palm.ContextFromYahooEOD(data) 
broker = SimulatedBroker(context, initial_deposit= 10000)
account = broker.get_cast_account()

closing_prices = data["Close"].to_numpy()
portfolio_value_history = []

while context.can_still_update():
    context.update()
    current_date_index = context.current_date_index()

    ## Wait till we have 30 days of data.
    if current_date_index <= 30:
        continue

    current_time = context.time_in_market_day()

    ## Only make trades at closing.
    if current_time == ContextEOD.TimeInMarketDay.Opening:
        continue
    
    previous_30_day_close = closing_prices[current_date_index-30:current_date_index]

    appl_current_price = context.current_market_price("AAPL")
    appl_previous_n_days = np.mean(previous_30_day_close)

    if (appl_current_price < appl_previous_n_days) and (appl_current_price < account.balance):
        broker.submit_order(MarketOrder.Buy("AAPL", quantity = 1))

    portfolio_value_history.append(broker.portfolio_value())

    