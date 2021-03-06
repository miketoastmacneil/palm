
from enum import Enum
import pprint

from palm.utils.generate_id import generate_hex_id

class MarketOrderType(Enum):
    BUY = 1
    SELL = 2

class MarketOrderStatus(Enum):
    OPEN = 1
    CLOSED = 2 
    NOT_SUBMITTED = 3

class MarketOrder:

    @staticmethod
    def Buy(symbol, quantity):
        return MarketOrder(MarketOrderType.BUY, symbol, quantity)

    @staticmethod
    def Sell(symbol, quantity):
        return MarketOrder(MarketOrderType.SELL, symbol, quantity)

    def __init__(self, type: MarketOrderType, symbol, quantity):

        self.id = generate_hex_id()

        self._type = type
        self._symbol = symbol
        self._quantity = quantity

        self.status = MarketOrderStatus.NOT_SUBMITTED
        self.time_submitted = None

        self.fulfilled = False
        self.time_closed = None
        self.position_id = None

    def set_as_submitted(self, time_submitted):
        self.status = MarketOrderStatus.OPEN
        self.time_submitted =  time_submitted
    
    def set_as_fulfilled(self, time, position_id):
        self.status = MarketOrderStatus.CLOSED
        self.fulfilled = True
        self.time_closed = time
        self.position_id = position_id

    @property
    def type(self):
        return self._type

    @property
    def symbol(self):
        return self._symbol

    @property
    def quantity(self):
        return self._quantity
    
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
            "Position Id": self.position_id,
            "Time Closed": self.time_closed
        }
        return pp.pformat(state)