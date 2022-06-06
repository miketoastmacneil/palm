from enum import Enum
import pprint

from .market_order import MarketOrder, MarketOrderType
from .daily_bar_context import ContextEOD
from .generate_id import generate_hex_id

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

    @staticmethod
    def from_order(context: ContextEOD, order: MarketOrder):
        quantity = order.quantity
        if order.type == MarketOrderType.SELL:
            quantity = int(-1.0 * quantity)

        return Position(context, order.symbol, quantity)

    def __init__(self, context: ContextEOD, symbol: int, quantity: int):

        self._context = context
        self.time_opened = context.current_time()

        self.id = generate_hex_id()
        self.status = Position.Status.OPEN
        self.time_closed = None
        self.have_already_been_closed: bool = False

        self.symbol = symbol
        self.quantity = quantity 

    def increase(self, amount):
        self.quantity += int(amount)

    def decrease(self, amount):
        self.quantity -= amount

    def set_to_closed(self):
        if self.have_already_been_closed:
            return
        else:
            self.have_already_been_closed = True
        self.time_closed = self._context.current_time()
        self.status = Position.Status.CLOSED
        return

    @property
    def current_dollar_value(self):
        return self._context.current_market_price(self.symbol) * self.quantity

    @property
    def state(self):
        return Position.Snapshot(self.side, self.symbol, self.quantity, self.current_dollar_value)

    @property
    def side(self):
        if self.quantity <= 0.0:
            return Position.Side.SHORT
        else:
            return Position.Side.LONG

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(str(self.id))

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent=4)
        state = {
            "Position Id": self.id,
            "Side": self.side,
            "Symbol": self.symbol,
            "Quantity": self.quantity,
            "Current Market Value": self.current_dollar_value,
            "Status": self.status,
        }
        return pp.pformat(state)

    class Snapshot:
        def __init__(self, side, symbol, quantity, current_dollar_value):
            self.side = side
            self.symbol = symbol
            self.quantity = quantity
            self.current_dollar_value = current_dollar_value

        def __repr__(self) -> str:
            pp = pprint.PrettyPrinter(indent=4)
            state = {
                "Side": self.side,
                "Symbol": self.symbol,
                "Quantity": self.quantity,
                "Market Value": self.current_dollar_value,
            }
            return pp.pformat(state)