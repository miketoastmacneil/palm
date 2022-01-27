
from ..context.daily_bar_context import ContextEOD
from .position import Position
from ..orders.market_order import MarketOrder

class LongPosition(Position):
    """
    A position is the holding of a quantity of an asset.
    It is the result of a successful order and subscribes
    to the context to update its current market value
    """

    def __init__(self, context: ContextEOD, order: MarketOrder):
        super(LongPosition, self).__init__(context) ## assigns context and opening time.

        self.order = order
        self.symbol = order.symbol
        self.quantity = order.quantity 
        self.side = Position.Side.LONG
    
    @property
    def current_dollar_value(self):
        return self._context.current_market_price(self.symbol)*self.quantity

    @current_dollar_value.setter
    def current_dollar_value(self):
        return
    def increase(self, additional_quantity):
        self.quantity += additional_quantity

    def decrease(self, amount_to_decrease):
        self.quantity -= amount_to_decrease