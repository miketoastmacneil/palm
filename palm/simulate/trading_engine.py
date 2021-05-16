
from palm.palm.simulate.holdings import Holdings
from typing import List

from .position import Position
from .synthetic_asset import SyntheticAsset


class TradingEngine:

    def __init__(self):

        self.holdings: List[Position] = None
        self.active_trades: List[Trades] = None
        self.cash_account: CashAccount = None

def rebalance_portfolio(alpha_model, current_holdings):


    ## The goal of the trading system is to take
    ## historical data as input to the alpha model, the 
    ## risk model and (can't remember the other one)
    ## The alpha model proposes trades, trades come in a single
    # unit, so one pair, one portfolio etc.
    # The portfolio optimization takes the risk model 
    # and the proposed trades and gives the accepted trades
    # with their respective weights.
    # The execution model executes the trades and updates our holdings.


    ## A position is a holding
    ## of an asset from a start time to and end time. 
    ## There is nothing which gives it trading rules or the like
    ## it is the result of a successful order, which is submitted
    ## to a broker and returns the affirmative that we are in
    ## the position.

    ## Notably, a position does not know WHY it was created.
    ## The logic behind why a position gets created is called
    ## a trade

    ## A trade encapsulates the logic of trading.
    ## It contains an asset, which could be synthetic or otherwise,
    ## and an exit rule.

    ## It can be either proposed, if the position hasn't been opened
    ## active, if the position is open, and completed, once the exit rule
    ## has been triggered

    ## The decision of whether or not to enter a trade belongs to portfolio optimization
    ## optimization or modeller.
    context: Context = None

    context = model.initialize_context()
    data = model.data_source()

    SyntheticAsset.context = context
    account = SimulatedBrokerageAccount(context.initial_investment)
    holdings = Holdings()


    ## This could be part of simulation history.
    # a separate class for logging and holding onto everything

    ## Log context has been set.
    for event in context:

        for position in holdings.current_positions():
            exit_signal = position.trade.exit_signal(context)
            if exit_signal == True:
                close_position_command = ClosePositionCommand(holdings, position)
                close_position.execute()
        
        proposed_trades = model.alpha_model(context, data)
        orders = model.optimize_portfolio(context, data, portfolio)
        positions = submit_orders(holdings, orders) ## This is where orders get executed. I.e. where you need an execution model.

        for position in position:
            open_position_command = OpenPositionCommand(holdings, position)
            open_position_command.execute()

    ## Update index
    context.current_time_index = 1

    for trade in self.current_trades:
        if trade.exit_rule(context) == True:
            self.execution.exit_trade(trade)

    proposed_trades = alpha_model.handle_data(context, data)



