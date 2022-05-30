from ..positions import Position
from .cash_account import CashAccount, DepositResult, WithdrawalResult
from ..orders import MarketOrder, MarketOrderType
from ..context import ContextEOD

class SimulatedBroker:
    def __init__(self, context: ContextEOD, initial_deposit: float, margin=2.0):

        self._cash_account = CashAccount(initial_deposit)
        self._positions_map = dict()
        self._orders = set()

        self._context = context

    def submit_order(self, order: MarketOrder):

        order.set_as_submitted(self._context.current_time())
        self._orders.add(order)
        if order.type == MarketOrderType.BUY:
            self._handle_buy_order(order)
        elif order.type == MarketOrderType.SELL:
            self._handle_sell_order(order)
        else:
            ValueError("Order type not recognized {}".format(order))

        return

    def liquidate_position(self, symbol):

        position = self.get_position(symbol)
        if position is None:
            return
        elif position.side == Position.Side.LONG:
            order = MarketOrder.Sell(symbol, position.quantity)
        elif position.side == Position.Side.SHORT:
            order = MarketOrder.Buy(symbol, abs(position.quantity))

        self.submit_order(order)
        return

    @property
    def all_positions(self):
        return self._positions_map

    @property
    def all_orders(self):
        return self._orders

    @property
    def cash_account(self):
        return self._cash_account

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self):
        raise RuntimeError("Cannot modify context at runtime.")

    def get_position(self, symbol):
        if symbol not in self._positions_map.keys():
            return None
        else:
            return self._positions_map[symbol]

    def portfolio_value(self):

        cash_value = self._cash_account.balance

        positions_value = 0.0
        for symbol in self._positions_map.keys():
            position = self._positions_map[symbol]
            if position.status == Position.Status.OPEN:
                positions_value += position.current_dollar_value

        return cash_value + positions_value

    def _handle_buy_order(self, order: MarketOrder):

        current_price = self._context.current_market_price(order.symbol)
        cost = current_price * order.quantity
        withdrawal_response = self._cash_account.submit_withdrawal_request(cost)

        if withdrawal_response.result == WithdrawalResult.APPROVED:
            order.set_as_fulfilled(self._context.current_time(), current_price)
            self._update_position(order)
        else:
            order.set_as_failed(withdrawal_response.reason)
            return 

        return

    def _handle_sell_order(self, order: MarketOrder):
        current_price = self._context.current_market_price(order.symbol)
        credit = current_price * order.quantity
        deposit_response = self._cash_account.submit_deposit_request(credit)
        if deposit_response.result == DepositResult.CONFIRMED:
            order.set_as_fulfilled(self._context.current_time(), current_price)
            self._update_position(order)
        else:
            order.set_as_failed(deposit_response.reason)
            return
        
    def _update_position(self, order):

        position = self.get_position(order.symbol)
        if position is None:
            new_position = Position.from_order(self._context, order)
            self._positions_map[order.symbol] = new_position
            return
        else:
            if order.type == MarketOrderType.SELL:
                position.decrease(order.quantity)
            elif order.type == MarketOrderType.BUY:
                position.increase(order.quantity)

        if position.quantity == 0:
            position.set_to_closed()
            del self._positions_map[order.symbol]
        return
