from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

import palm as pm

start_date, end_date, look_back = (
    datetime(2020, 6, 1),
    datetime(2020, 10, 1),
    timedelta(weeks=8),
)

symbol_list = ["AAPL", "MSFT"]
backtest = pm.BacktestSession(symbol_list, start_date, end_date, look_back)

is_close = (
    lambda time_event: time_event.time_in_market_day == pm.TimeInMarketDay.Closing
)
for time_event in filter(lambda event: is_close(event), backtest.events()):
    ## Same code here. That should be all thats needed.
    backtest.trader.liquidate_all_positions()
    t = time_event.date_index_since_start
    previous_closing_prices = backtest.historical_data["Close"].to_numpy()[t - 1, :]
    current_closing_prices = backtest._context.current_market_prices().to_numpy()

    returns_since_yesterday = (
        current_closing_prices - previous_closing_prices
    ) / previous_closing_prices
    percent_returns = returns_since_yesterday / np.sum(np.abs(returns_since_yesterday))
    median_return = np.median(percent_returns)

    order_quantity = dict()
    for i in range(len(returns_since_yesterday)):
        normalizer = np.sum(np.abs(percent_returns - median_return))
        amount_to_invest = (
            -(percent_returns[i] - median_return)
            * backtest.trader.cash_balance
            / normalizer
        )
        order_quantity[symbol_list[i]] = int(
            round(
                amount_to_invest
                / backtest._context.current_market_price(symbol_list[i])
            )
        )

    backtest.trader.submit_trade(order_quantity)

plt.plot(backtest.portfolio_value())
plt.plot(backtest.historical_data.close_prices())
plt.show()
