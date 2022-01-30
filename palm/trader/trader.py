
from ..context.context_observable import ContextObservable
from ..broker.simulated_broker import SimulatedBroker
from ..utils.generate_id import generate_hex_id
from ..trades.trade import Trade

class SimulatedTrader:
    """
    Handles the logic for submitting and closing out trades
    which are more complicated than a single asset.

    """

    def __init__(self, context: ContextObservable, initial_deposit):

        self.open_trades = []
        self.closed_trades = []
        self._context = context 
        self.broker = SimulatedBroker(context, initial_deposit)
        self._id = generate_hex_id()

        self._context.add_observer(self._id, self.on_context_update)

        return

    def submit_trade(self, trade: Trade):

        trade.submit_entry_order(self.broker)
        self.open_trades.append(trade)

        return

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
