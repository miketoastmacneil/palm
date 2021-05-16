
import numpy as np
from abc import ABC, ABCMeta, abstractmethod

from .context import Context
from .data_source import DataSource
from .holdings import Holdings
from .orders import CloseOrder, OpenOrder
from .position import Position

class AlphaModel:

    @abstractmethod
    def get_orders(self, history):
        pass

    @property
    @abstractmethod
    def look_back(self):
        pass



class SimResults:

    def __init__(self, portfolio_dollar, portfolio_shares, trades_dollar, trades_shares):

        self.portfolio_dollar = portfolio_dollar
        self.portfolio_shares = portfolio_shares
        self.trades_dollar = trades_dollar
        self.trades_shares = trades_shares

        return


## Look from one period to the next.
## Instead of updating holdings, we update the position values.


def run_simulation(data_source: DataSource, alpha_model: AlphaModel):
    """
    Backtest based on a striped down version of convex optimization
    for multi-period portfolio optimization.

    """

    T, N = data_source.shape
    symbol_to_index_map = data_source.symbol_to_index

    alpha_model = alpha_model
    data_source = data_source

    portfolio_dollar = np.zeros((T, N))   ## dollar value of positions at each time.
    portfolio_shares = np.zeros((T, N))  ## number of shares in each asset at time t.

    trades_dollar = np.zeros((T, N))
    trades_shares = np.zeros((T, N))

    post_trade_portfolio_dollar = np.zeros((T, N))

    look_back = alpha_model.look_back

    portfolio: Holdings
    post_trade_portfolio: Holdings
    current_positions = []
    historical_positions = []

    context:  Context  = None
    holdings: Holdings = None
    
    for t in range(T):

        context.step()
        if t < look_back+1:
            continue

        ## Update from previous period
        portfolio_dollar[t,:] = post_trade_portfolio_dollar[t-1,:]+data_source.returns[t]*post_trade_portfolio_dollar[t-1,:]
        portfolio_shares[t,:] = portfolio_shares[t,:]+trades_shares[t-1,:]

        historical_returns = data_source.returns[t-look_back-1:t-1] ## indexing needs to be up too and including.
        historical_prices = data_source.prices[t-look_back:t]

        historical_data = context.historical_data(look_back)
        ## Alpha model takes historical data and the set of current
        ## positions and submits open or close orders. 
        ## Ideally, the alpha model should return a set of open or close signals.
        ## The portfolio optimization module would turn these into buy and sell orders.
        ## Here we don't care and skip optimization
        orders = alpha_model.get_orders(historical_data, holdings)

        ## This is rebalancing the book
        for order in orders:
            if order.to_close:
                holdings.remove(order.position_id)
            if order.to_open:
                holdings.add(Position(order.shares_to_order))
        ## We have the current prices here.

        ## Doesn't submit to broker, just gives the amount
        ## you want at the price you want.
        trades_shares[t,:] = share_amount_orders
        trades_dollar[t,:] = share_amount_orders*historical_prices[-1] ## most recent prices.

        post_trade_portfolio_dollar[t,:] = portfolio_dollar[t,:]+trades_dollar[t,:]

    return SimResults(portfolio_dollar, portfolio_shares, trades_dollar, trades_shares) 


            

