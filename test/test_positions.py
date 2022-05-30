from tracemalloc import Snapshot
from turtle import pos
from palm.positions.position import Position
import pytest

import pandas as pd

from palm.orders import MarketOrder
from palm.data import polygon_symbol_indexed_to_OHCLV_indexed, EquityEOD
from palm.context import ContextEOD

## TODO: Would be useful to have some mock data to load.
@pytest.fixture
def buy_order():
    return MarketOrder.Buy("MSFT", 1)

@pytest.fixture
def sell_order():
    return MarketOrder.Sell("MSFT", 1)

@pytest.fixture
def eod_data():

    data = {}
    data["AAPL"] = pd.read_csv("sample_data/AAPL-Sample-Data.csv", index_col=0)
    data["MSFT"] = pd.read_csv("sample_data/MSFT-Sample-Data.csv", index_col=0)

    return EquityEOD(polygon_symbol_indexed_to_OHCLV_indexed(data))

@pytest.fixture
def context(eod_data):
    return ContextEOD(eod_data)

def test_BuyOrder_LongPositionConstructed(context, buy_order):

    position = Position.from_order(context, buy_order)
    assert position.side == Position.Side.LONG
    assert position.status == Position.Status.OPEN
    assert position.quantity == 1
    assert type(position.quantity) == int
    assert position.current_dollar_value == context.current_market_price("MSFT")
    assert position.have_already_been_closed == False

def test_LongPositionIncreased_QuantityIncreased(context, buy_order):
    position = Position.from_order(context, buy_order)

    position.increase(1)
    assert position.quantity == 2

def test_LongPositionDecreased_QuantityDecreased(context, buy_order):

    position = Position.from_order(context, buy_order)
    position.decrease(1)
    assert position.quantity == 0

def test_LongPositionDecreasedToZero_StatusSetToClosed(context, buy_order):

    position = Position.from_order(context, buy_order)
    position.decrease(1)
    assert position.quantity == 0

def test_SellOrder_ShortPositionConstructed(context, sell_order):

    position = Position.from_order(context, sell_order)
    assert position.side == Position.Side.SHORT
    assert position.status == Position.Status.OPEN
    assert position.quantity == -1
    assert position.current_dollar_value == -1.0 * context.current_market_price("MSFT")
    assert position.have_already_been_closed == False

def test_ShortPositionIncreased_QuantityDecreased(context, sell_order):

    position = Position.from_order(context, sell_order)
    position.decrease(1)
    assert position.quantity == -2

def test_ShortPositionIncreased_QuantityIncreased(context, sell_order):

    position = Position.from_order(context, sell_order)
    position.increase(1)
    assert position.quantity == 0

def test_ShortPositionDecreasedToZero_StatusSetToClosed(context, sell_order):

    position = Position.from_order(context, sell_order)
    position.increase(1)
    assert position.quantity == 0

def test_PositionDecreased_SnapshotRemainsUnchanged(context, buy_order):
    
    position = Position.from_order(context, buy_order)
    snapshot = position.state
    quantity = snapshot.quantity

    position.decrease(1)
    snapshot.quantity == quantity
