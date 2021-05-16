

from .position import Position
from .universe import EquityUniverse

class Holdings:
    """
    Abstraction for a set of positions in assets and a cash account.
    
    Lets you add a position, liquidate one, check the available
    cash balance. 

    It also calculates the current total portfolio value 
    at each given point in time.
    """

    universe: EquityUniverse = None

    def __init__(self, initial_cash_deposited): 
        self.current_position_map: Dict[str, Position] = None
        self.historical_position_map: Dict[str, Position] = None
        self.cash_account = None

        return

    def available_cash(self):
        return self._available_cash

    def add(self, position: Position):
        self.current_position_map[position.id] = position 

    def liquidate(self, position_id):
        if position_id not in self.current_position_map.keys():
            raise RuntimeError("Trying to remove a non-existent position.")
        self.current_position_map[position_id].close()
        self.historical_position_map[position_id] = self.current_position_map[position_id]
        del self.current_position_map[position_id]
