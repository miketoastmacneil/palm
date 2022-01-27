from abc import abstractmethod
from enum import Enum
import pprint
from typing import Dict

from ..context.daily_bar_context import ContextEOD
from ..orders.market_order import MarketOrder
from ..utils.generate_id import generate_hex_id

class Position:
    """
    A position is the holding of a quantity of an asset.
    It is the result of a successful order 
    and the current market value is given by the context.
    """

    class Status(Enum):
        OPEN = 1
        CLOSED = 2

    class Side(Enum):
        LONG = 1
        SHORT = 2

    def __init__(self, context: ContextEOD):

        self._context = context
        self.time_opened = context.current_time()

        self.id = generate_hex_id()
        self.status = Position.Status.OPEN
        self.time_closed = None
        self.have_already_been_closed: bool = False

    def set_to_closed(self):
        if self.have_already_been_closed:
            return
        else:
            self.have_already_been_closed = True
        self.time_closed = self._context.current_time()
        self.status      = Position.Status.CLOSED
        return

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(str(self.id))

    @abstractmethod
    def increase(self, amount):
        pass

    @abstractmethod
    def decrease(self, amount):
        pass

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent = 4)
        state = {
            "Position Id": self.id,
            "Side": self.side,
            "Symbol": self.symbol,
            "Quantity": self.quantity,
            "Current Market Value": self.current_dollar_value,
            "Status": self.status,
        }
        return pp.pformat(state)