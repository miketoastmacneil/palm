

from typing import Callable

from .synthetic_asset import SyntheticAsset
from .context import Context

class Trade:
    """
    A trade is the logic behind what positions
    to open. It includes an asset as well the exit
    logic.

    Trades are created (proposed) in the alpha model.
    They are accepted by the portfolio optimization mode
    """

    class Status:
        Proposed = 1
        Active = 2
        Complete = 3

    def __init__(self, asset: SyntheticAsset, exit_rule: Callable[[SyntheticAsset, Context], bool]):
        self.status       = Trade.Status.Proposed
        self.asset        = asset 
        self._exit_rule   = exit_rule 
        self._position_id = None

    def transition_to_active(self, position_id):
        self._position_id = position_id
        self.status = Trade.Status.Active

    def transition_to_completed(self):
        self.status = Trade.Status.Complete
    
    def check_exit_rule(self, context: Context):

        return self._exit_rule(self.asset, context)
