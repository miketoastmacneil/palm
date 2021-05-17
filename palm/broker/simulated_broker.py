
from ..trades.trade import Trade
from ..utils.generate_id import generate_hex_id
from ..positions.position import Position
from ..positions.long_position import LongPosition
from ..positions.short_position import ShortPosition
from .cash_account import CashAccount
from ..orders.market_order import MarketOrder, MarketOrderType
from ..context.daily_bar_context import ContextEOD

class SimulatedBroker:

    def __init__(self, context: ContextEOD, initial_deposit: float, margin = 2.0):

        self._cash_account = CashAccount(initial_deposit)
        self._margin = margin
        self._positions_map = dict()
        self._orders = set()
        self._id = generate_hex_id()

        self._context = context
        self._context.add_observer(self._id, self.on_context_update)
        self._trades = []

    def submit_order(self, order: MarketOrder):

        order.set_as_submitted(self._context.current_time())
        self._orders.add(order)
        self._process_order_at_current_price(order)
        
        return

    def _process_order_at_current_price(self, order: MarketOrder):
        
        position = self.get_position(order.symbol)
        if position is None:
            self._open_position(order)
        else:
            self._modify_position(order, position)

    def _open_position(self, order: MarketOrder):

        if order.type == MarketOrderType.BUY:
            cost = self._context.current_market_price(order.symbol)*order.quantity
            self._cash_account.withdraw(cost)
            position = LongPosition(self._context, order)
        if order.type == MarketOrderType.SELL:
            credit = self._context.current_market_price(order.symbol)*order.quantity
            self._cash_account.deposit(credit)
            position = ShortPosition(self._context, order)

        order.set_as_fulfilled(self._context.current_time(), position.id)
        self._positions_map[position.symbol] = position

    def _modify_position(self, order: MarketOrder, position: Position):

        if (order.type == MarketOrderType.BUY) and (position.side == Position.Side.LONG) :
            cost = self._context.current_market_price(order.symbol)*order.quantity
            self._cash_account.withdraw(cost)
            position.increase(order.quantity)
        if (order.type == MarketOrderType.SELL) and (position.side == Position.Side.LONG):
            credit = self._context.current_market_price(order.symbol)*order.quantity
            self._cash_account.deposit(credit)
            position.decrease(order.quantity)

        if (order.type == MarketOrderType.BUY) and (position.side == Position.Side.SHORT) :
            cost = self._context.current_market_price(order.symbol)*order.quantity
            self._cash_account.withdraw(cost)
            position.decrease(order.quantity)
        if (order.type == MarketOrderType.SELL) and (position.side == Position.Side.SHORT):
            credit = self._context.current_market_price(order.symbol)*order.quantity
            self._cash_account.deposit(credit)
            position.increase(order.quantity)

        order.set_as_fulfilled(self._context.current_time(), position.id)
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
        position.set_to_closed()

        return

    def get_positions(self):
        return self._positions_map

    def get_orders(self):
        return self._orders

    def get_cast_account(self):
        return self._cash_account

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

    def on_context_update(self):

        for trade in self._trades:
            if (trade.status == Trade.Status.ACTIVE) and (trade.exit_rule_triggered()):
                trade.submit_exit_order(self)

    def submit_trade(self, trade: Trade):

        self._trades.append(trade)
        trade.submit_entry_order(self)