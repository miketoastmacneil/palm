
from abc import abstractmethod
from palm.palm.simulate.daily_bar_context import ContextEOD
from typing import List

from .data_source import DataSource
from .synthetic_asset import SyntheticAsset
from .trade import Trade
from .context import Context

import numpy as np

class AlphaModel:

    @abstractmethod
    def create_context(self) -> Context:
        pass

    @abstractmethod
    def handle_data(self) -> List[Trade]:
        pass


class BuyOnTheGap:

    def __init__(self) -> None:
        return

    def create_context(self) -> Context:
        """
        Right now just instantiate with Yahoo finance
        EOD data.
        """
        ## Should pull in the data that is needed to 
        ## Make trades

        context = ContextEOD 
        ## Add start date and end date.


    def handle_data(self, context: Context, data: DataSource) -> List[Trade]:

        proposed_trades = []
        return_data = data.closing
        _, N = data.shape

        trade_time_index = context.current_time_index
        next_close_time = context.next_close

        trade_next_period = lambda context: context.current_time == next_close_time

        ## Trading at the next close

        for i in range(N):
            std = np.std(return_data[:,i])
            if return_data[-1,i] > std:
                trade_asset = SyntheticAsset({data.symbols(i): 1})
                proposed_trades.append(
                    Trade(
                        trade_asset, 
                        exit_rule = trade_next_period 
                    )
                )

        return proposed_trades
