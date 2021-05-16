
from enum import Enum
from typing import Dict

from .context import Context
from .synthetic_asset import SyntheticAsset
from .utils import generate_hex_id

class Position:
    """
    A position is a record of a holding of an asset from
    a start time to and end time. It can only be created
    as a result of a successful order. It is
    also linked to an active trade.
    """

    class Status(Enum):
        OPEN = 1
        CLOSED = 2

    def __init__(self, asset: SyntheticAsset):

        self.id = generate_hex_id()

        self.status: Position.Status        = Position.Status.OPEN
        self.have_already_been_closed: bool = False
        self.time_index_opened: int         = Position.context.current_time_index ## Needs to know what time it ist.
        self.time_index_closed: int         = None

        self.asset = asset

        self.asset.add_observer(self.id, self._update_dollar_value_history)
        self.dollar_value_history: List[float] = []
        self._update_dollar_value_history()

    def close(self):
        if self.have_already_been_closed:
            return
        else:
            self.have_already_been_closed = True
        self.time_index_closed = Position.context.current_time_index
        self.status            = Position.Status.CLOSED
        self.asset.remove_observer(self.id)
        return

    def _update_dollar_value_history(self):
        
        self.dollar_value_history.append(self.asset.current_dollar_value)

        return

