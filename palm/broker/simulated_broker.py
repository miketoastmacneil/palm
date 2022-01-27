
from turtle import pos
from urllib import response
from ..trades.trade import Trade
from ..utils.generate_id import generate_hex_id
from ..positions import Position, LongPosition, ShortPosition
from .cash_account import CashAccount, DepositResult, WithdrawalResult
from ..orders import MarketOrder, MarketOrderType
from ..context import ContextEOD

class SimulatedBroker:

    def __init__(self, context: ContextEOD, initial_deposit: float, margin = 2.0):

        self._cash_account = CashAccount(initial_deposit)
        self._positions_map = dict()
        self._orders = set()
        self._id = generate_hex_id()
        self._positions_history = set()

        self._context = context

    def submit_order(self, order: MarketOrder):

        order.set_as_submitted(self._context.current_time())
        self._orders.add(order)
        self._process_order_at_current_price(order)
        
        return

    def liquidate_position(self, symbol):

        position = self.get_position(symbol)
        if position is None:
            return
        if position.side == Position.Side.LONG:
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
            if position.status==Position.Status.OPEN: 
                positions_value += position.current_dollar_value
    
        return cash_value+positions_value

    def _process_order_at_current_price(self, order: MarketOrder):
        
        position = self.get_position(order.symbol)
        if position is None:
            self._open_position(order)
        else:
            self._modify_position(order, position)

    def _open_position(self, order: MarketOrder):

        position = None
        current_price = self._context.current_market_price(order.symbol)
        if order.type == MarketOrderType.BUY:
            cost = current_price * order.quantity
            response = self._cash_account.submit_withdrawal_request(cost)
            if response.result == WithdrawalResult.APPROVED:
                position = LongPosition(self._context, order)
            else:
                order.set_as_failed(self._context.current_time())
                return
        if order.type == MarketOrderType.SELL:
            credit = self._context.current_market_price(order.symbol)*order.quantity
            response = self._cash_account.submit_deposit_request(credit)
            if response.result == DepositResult.CONFIRMED:
                position = ShortPosition(self._context, order)
            else:
                order.set_as_failed(self._context.current_time())
                return

        if position is not None: 
            order.set_as_fulfilled(self._context.current_time(), current_price)
            self._positions_map[position.symbol] = position

    def _modify_position(self, order: MarketOrder, position: Position):

        if (order.type == MarketOrderType.BUY) and (position.side == Position.Side.LONG) :
            self._handle_increase_long_position(order, position)
            
        if (order.type == MarketOrderType.SELL) and (position.side == Position.Side.LONG):
            self._handle_decrease_long_position(order, position)

        if (order.type == MarketOrderType.BUY) and (position.side == Position.Side.SHORT) :
            self._handle_decrease_short_position(order, position)

        if (order.type == MarketOrderType.SELL) and (position.side == Position.Side.SHORT):
            self._handle_increase_short_position(order, position)

        return


    def _handle_increase_long_position(self, order: MarketOrder, position):
        
        current_price = self._context.current_market_price(order.symbol) 
        cost = current_price * order.quantity
        response = self._cash_account.submit_withdrawal_request(cost)
        if response.result == WithdrawalResult.APPROVED:
            position.increase(order.quantity)
            order.set_as_fulfilled(self.context.current_time(), current_price)
        else:
            order.set_as_failed(self._context.current_time(), response.reason)
            return

    def _handle_decrease_long_position(self, order: MarketOrder, position: LongPosition):

        if order.quantity > position.quantity:
            raise ValueError("Order to sell exceeds number of shares.")
        current_price = self._context.current_market_price(order.symbol) 
        credit = current_price * order.quantity
        response = self._cash_account.submit_deposit_request(credit)
        if response.result == DepositResult.CONFIRMED:
            if order.quantity == position.quantity:
                position.decrease(order.quantity)
                position.set_to_closed()
                self._positions_history.add(position)
                del self._positions_map[position.symbol]
            else:
                position.decrease(order.quantity)
        else:
            order.set_as_failed(self._context.current_time(), response.reason)
        return

    def _handle_increase_short_position(self, order, position):

        current_price = self._context.current_market_price(order.symbol)
        credit = current_price * order.quantity
        response = self._cash_account.submit_deposit_request(credit)
        if response.result == DepositResult.CONFIRMED:
            position.increase(order.quantity)
            order.set_as_fulfilled(self.context.current_time(), current_price)
        else:
            order.set_as_failed(self._context.current_time(), response.reason)

    def _handle_decrease_short_position(self, order, position):

        if order.quantity > position.quantity:
            raise ValueError("""
                Order to decrease short position is buying too many shares.
                Liquidate the position and open a new long position.
            """)
        current_price = self._context.current_market_price(order.symbol)
        cost = current_price * order.quantity
        response = self._cash_account.submit_withdrawal_request(cost)
        if response.result == WithdrawalResult.APPROVED:
            if order.quantity == position.quantity:
                position.decrease(order.quantity)
                position.set_to_closed()
                self._positions_history.add(position)
            else: 
                position.decrease(order.quantity)
            order.set_as_fulfilled(self.context.current_time(), current_price)
        else:
            order.set_as_failed(self._context.current_time(), response.reason)
            return