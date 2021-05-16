
from .daily_bar_context import ContextEOD
from ..broker.simulated_broker import SimulatedBroker

class Simulator:

    def __init__(self, context: ContextEOD, intial_deposit: float):
        
        self.context = context
        self.broker = SimulatedBroker(initial_deposit, context, self)
        self.order_history = []
        self.position_history = []

    def _on_order_submitted(self, order):
        self.order_history.append(order)
        return

    def _on_position_opened(self, position):
        self.position_history.append(position)
        return
