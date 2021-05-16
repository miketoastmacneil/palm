
import palm
from palm.orders import MarketOrder

# Would still want to accomodate being able to track individual trades
# and work conveniently with arrays


## Try to figure out an actual algorithm you'd like to simulate

## Passing in data lets me work directly with the dataframe 
## outside of the simulator, its a bit easier.



context = palm.ContextFromYahooEOD(data) 
simulator = palm.simulator(context, initial_deposit = 10000)
broker = simulator.get_brokerage_account()
account = broker.get_account()

while context.can_still_update():
    context.update()
    current_date_index = context.current_date_index

    previous_30_day_close = data["Adj Close"][current_date_index-30:current_date_index]

    appl_current_price = context.current_price("AAPL")
    appl_previous_n_days = np.mean(previous_30_day_close)

    if (appl_current_price < appl_previous_n_days) and (appl_current_price < account.buying_power):
        broker.submit_order(MarketOrder.buy("AAPL", quantity = 1))

    ## Do I want to see at the end? Positions.


    