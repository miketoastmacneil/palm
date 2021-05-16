

from .data_source import DataSource
from .synthetic_asset import SyntheticAsset
from .trade import Trade
from .context import Context

class ExitStrategy:

    def __init__(self, stop_loss, take_profit, max_open_time):
        self._stop_loss     = stop_loss
        self._take_profit   = take_profit
        self._max_open_time = max_open_time


    def __call__(self, asset: SyntheticAsset, context: Context):
        if asset.current_dollar_value() > self._take_profit:
            return True
        if context.current_time_index == self._max_open_time:
            return True
        if asset.current_dollar_value() < self._stop_loss:
            return True
        else:
            False

class PairsTrade:

    def propose_trades(self, context: Context, data: DataSource):

        proposed_trades = []

        pair = SyntheticAsset({"JPM": 4, "KBE":-9})

        ## Suppose we can 
        ## for pairs in pairs, get the 
        ## mean reversion time, entry signal can be handled here.
        trade_time_index = context.current_time_index

        ## suppose we can get standard deviation from
        ## from historical data somehow.
        stop_time_index = trade_time_index + 5

        std_dev = None
        
        if pair.current_dollar_value() > 2*std_dev:
            trade = Trade(
                pair, 
                ExitStrategy(4*std_dev, 0.5*std_dev, stop_time_index)
            )
            proposed_trades.append(trade)

