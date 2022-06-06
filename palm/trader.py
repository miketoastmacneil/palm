from typing import Set
import numpy as np

from typing import Dict

from .position import Position
from .context_observable import ContextObservable
from .simulated_broker import SimulatedBroker
from .generate_id import generate_hex_id
from .trade import Trade

def weights_as_a_percentage_of_total_portfolio_value(positions: Dict[str, Position], portfolio_value: float, cash_balance: float):

    weights = {}
    for position_symbol in positions.keys():
        weights[position_symbol] = positions[position_symbol].current_dollar_value / portfolio_value

    weights["Cash"] = cash_balance

    return weights

class SimulatedTrader:
    """
    A layer above the broker to offer more 
    and convenient methods for quant algorithms. Keeps track of
    "trades" which are a single unit intended to be
    """
    class Snapshot:
        def __init__(self, position_snapshot, portfolio_value, cash_balance):
            self.positions = position_snapshot
            self.portfolio_value = portfolio_value
            self.cash_balance = cash_balance

    def __init__(self, context: ContextObservable, initial_deposit):

        self.open_trades = []
        self.closed_trades = []
        self._context = context
        self.broker: SimulatedBroker = SimulatedBroker(context, initial_deposit)
        self._id = generate_hex_id()

        self._context.add_observer(self._id, self.on_context_update)

        return

    def submit_trade(self, trade: Trade):

        if type(trade) == dict:
            trade = Trade(trade)
        trade.submit_entry_order(self.broker)
        self.open_trades.append(trade)

        return

    def rebalance_to_weights(self, target_weights):
        """
        Targets are expcected to be an N+1 vector where the 
        final entry the amount to be allocated to cash.
        """

        symbol_list = self._context._data.symbols
        broker_weights = weights_as_a_percentage_of_total_portfolio_value(self.broker)
        current_weights = np.zeros(len(symbol_list) + 1)  ## N+1, final entry is cash

        for i, symbol in enumerate(symbol_list):
            if symbol in broker_weights.keys():
                current_weights[i] = broker_weights[symbol]

        current_weights[-1] = self.cash_balance

        diff = target_weights - current_weights
        order_sizes = np.round(
            diff[:-1] 
            * self.broker.portfolio_value()
            / self._context.current_market_prices()
        )
        trade_dict = dict(
            [(key, value) for key, value in zip(symbol_list, order_sizes)]
        )

        self.submit_trade(trade_dict)

        return

    @property
    def cash_balance(self):
        return self.broker.cash_account.balance

    def liquidate_all_positions(self):

        for trade in self.open_trades:
            if trade.status == Trade.Status.ACTIVE:
                trade.submit_exit_order(self.broker)
                self.closed_trades.append(trade)
                self.open_trades.remove(trade)

    def on_context_update(self):

        for trade in self.open_trades:
            if (trade.status == Trade.Status.ACTIVE) and (trade.exit_rule_triggered()):
                trade.submit_exit_order(self.broker)
                self.closed_trades.append(trade)
                self.open_trades.remove(trade)

    @property
    def state(self):
        positions = {key:self.broker.all_positions[key].state for key in self.broker.all_positions}
        portfolio_value = self.broker.portfolio_value()
        cash = self.broker.cash_account.balance
        return SimulatedTraderSnapshot(
            positions,
            portfolio_value,
            cash
        )
