
from palm.backtestsession import BacktestSessionSubscribe
from palm.broker.simulated_broker import SimulatedBroker
from palm.data.equity_eod import EquityEOD
import pytest

import pandas as pd

from palm.data import polygon_symbol_indexed_to_OHCLV_indexed
from palm.context import ContextEOD