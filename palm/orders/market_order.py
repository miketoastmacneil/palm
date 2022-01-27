
from enum import Enum
import pprint

from palm.utils.generate_id import generate_hex_id

class MarketOrderType(Enum):
    BUY = 1
    SELL = 2

class MarketOrderStatus(Enum):
    NOT_SUBMITTED = 3
    SUBMITTED = 4
    CLOSED = 2 
    FAILED = 5

class MarketOrder:

    @staticmethod
    def Buy(symbol, quantity):
        return MarketOrder(MarketOrderType.BUY, symbol, quantity)

    @staticmethod
    def Sell(symbol, quantity):
        return MarketOrder(MarketOrderType.SELL, symbol, quantity)

    def __init__(self, type: MarketOrderType, symbol, quantity):

        self.id = generate_hex_id()

        if quantity <= 0:
            raise ValueError("Market Order Quantity must be postive.")

        self._type = type
        self._symbol = symbol
        self._quantity = quantity

        self.status = MarketOrderStatus.NOT_SUBMITTED
        self.time_submitted = None

        self.fulfilled = False
        self.time_closed = None
        self.failure_reason = None
        self.avg_price = None

    def set_as_submitted(self, time_submitted):
        self.status = MarketOrderStatus.SUBMITTED
        self.time_submitted =  time_submitted
    
    def set_as_fulfilled(self, time, avg_price):
        self.status = MarketOrderStatus.CLOSED
        self.fulfilled = True
        self.time_closed = time
        self.avg_price = avg_price

    def set_as_failed(self, reason):
        self.status = MarketOrderStatus.FAILED
        self.failure_reason = reason

    @property
    def type(self):
        return self._type

    @property
    def symbol(self):
        return self._symbol

    @property
    def quantity(self):
        return self._quantity

    def __eq__(self, other)->bool:
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent = 4)
        state = {
            "Order Id": self.id,
            "Status": self.status,
            "Type": self.type,
            "Symbol": self.symbol,
            "Quantity": self.quantity,
            "Fulfilled": self.fulfilled,
            "Time Submitted": self.time_submitted,
            "Average Price": self.avg_price,
            "Time Closed": self.time_closed
        }
        return pp.pformat(state)