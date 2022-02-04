
from enum import Enum
import pprint
from typing import Callable, Dict

from palm.utils.generate_id import generate_hex_id

from ..orders.market_order import MarketOrder

class Trade:

    class Status(Enum):
        INACTIVE = 1
        ACTIVE = 2
        COMPLETE = 3

    def __init__(self, number_of_shares: Dict[str, int], exit_rule: Callable = None):

        self.id = generate_hex_id()
        self._shares = number_of_shares
        self._exit_rule = exit_rule
        self._entry_orders = []
        self._exit_orders = []

        self.status = Trade.Status.INACTIVE
        self._context = None
        self._trade_complete = False
        self._initial_value = 0.0
        self._exit_value = 0.0

    def submit_entry_order(self, broker):

        self._context = broker._context

        for symbol in self._shares.keys():
            quantity = self._shares[symbol]
            order = None
            if quantity < 0:
                order = MarketOrder.Sell(symbol, abs(quantity))
            elif quantity > 0:
                order = MarketOrder.Buy(symbol, abs(quantity))
            else:
                continue

            self._entry_orders.append(order)

        ## By default, want to do all the selling before the buying. 
        sorted(self._entry_orders, key=lambda order: order.quantity)
        for order in self._entry_orders:
            broker.submit_order(order)
         
        self.status = Trade.Status.ACTIVE 
        self._initial_value = self.current_market_value()

        return

    def submit_exit_order(self, broker):

        for symbol in self._shares.keys():
            quantity = self._shares[symbol]
            order = None
            if quantity > 0:
                order = MarketOrder.Sell(symbol, abs(quantity))
            elif quantity < 0:
                order = MarketOrder.Buy(symbol, abs(quantity))
            else:
                continue
            
            self._exit_orders.append(order)

        sorted(self._exit_orders, key=lambda order: order.quantity)
        for order in self._exit_orders:
            broker.submit_order(order)

        self._exit_value = self.current_market_value()
        self.status = Trade.Status.COMPLETE
        self._context = None
        self._trade_complete = True
        return

    def exit_rule_triggered(self):
        if self._exit_rule is None:
            return False
        else:
            return self._exit_rule()

    def current_market_value(self):

        if self.status == Trade.Status.INACTIVE:
            return 0.0
        elif self.status == Trade.Status.ACTIVE:
            value = 0.0
            for symbol in self._shares.keys():
                quantity = self._shares[symbol]
                value += self._context.current_market_price(symbol)*quantity
            return value
        elif self.status == Trade.Status.COMPLETE:
            return self._exit_value - self._initial_value
        else:
            raise RuntimeError("Trade Status not recognized.")

    def profit_and_loss(self):
        if self.status == Trade.Status.INACTIVE:
            return 0.0 
        if self.status == Trade.Status.ACTIVE:
            return self.current_market_value()-self._initial_value
        if self.status == Trade.Status.COMPLETE:
            return self._exit_value- self._initial_value
        else:
            raise RuntimeError("Trade Status not recognized.")

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent = 4)
        state = {
            "Status": self.status,
            "Initial Value": self._initial_value,
            "Exit Value": self._exit_value,
            "Profit and Loss": self.profit_and_loss(),
            "Assets": self._shares,
        }
        return pp.pformat(state)