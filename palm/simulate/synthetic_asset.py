
import pprint
from typing import Callable
from typing import Dict

from .context import Context
from .utils import generate_hex_id

class SyntheticAsset:
    """
    A Synthetic Asset is a set of holdings in assets selected from a 
    universe. The synthetics assets value is updated by
    observing the context. So the synthetic asset is an observer. 

    The reason for having this abstraction is several quant strategies
    trade long-short (or just long) portfolios of assets and have 
    trading rules based on how those holdings behave as if they were
    a single asset. In palm, all positions and trades are based on Synthetic assets.
    """
    context: Context = None

    def __init__(self, number_of_shares: Dict[str, int]):

        if SyntheticAsset.context is None:
            raise RuntimeError("Context needs to be created to create an asset.")
    
        for symbol in number_of_shares.keys():
            if symbol not in SyntheticAsset.context.symbols:
                raise RuntimeError("Symbol not in current context.")

        self.id = generate_hex_id()
        self._number_of_shares = number_of_shares
        self._value = 0.0
        for symbol in self._number_of_shares.keys():
            self._value += self._number_of_shares[symbol]*SyntheticAsset.context.current_price(symbol)

        ## Keep a list of positions as observers.
        ## These need to update their history based on the price.
        self._observers: Dict[str, Callable] = dict()
        ## Add myself to the context list of observers
        SyntheticAsset.context.add_observer(self.id, self._update_current_value)

    def current_dollar_value(self):
        return self._value

    def add_observer(self, observer_id, observer_callable):
        if observer_id in self._observers.keys():
            return
        else:
            self._observers[observer_id] = observer_callable

    def remove_observer(self, observer_id):
        if not observer_id in self._observers.keys():
            return
        else:
            del self._observers[observer_id]

    def _update_current_value(self):

        value = 0.0
        for symbol in self._number_of_shares.keys():
            value += SyntheticAsset.context.current_price(symbol)*self._number_of_shares[symbol]

        self._value = value
        for observer_id in self._observers.keys():
            self._observers[observer_id]()

    def __eq__(self, other) -> bool:
        if self._number_of_shares.keys()!= other._number_of_shares.keys():
            return False

        same_number_of_shares = True
        for symbol in self._number_of_shares.keys():
            if self._number_of_shares[symbol]!=other._number_of_shares[symbol]:
                same_number_of_shares = False

        return same_number_of_shares

    def __repr__(self) -> str:
        pp = pprint.PrettyPrinter(indent = 4)
        state = {
            "Assets": list(self._number_of_shares.keys()),
            "Current Total Price": self.current_dollar_value()
        }
        return pp.pformat(state)