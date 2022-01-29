 
from turtle import pos
from palm.positions.long_position import LongPosition
from palm.positions.position import Position
from palm.positions.short_position import ShortPosition
import pytest

import pandas as pd

from palm.orders import MarketOrder
from palm.data import PolygonEOD
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

    return PolygonEOD(data)

@pytest.fixture
def context(eod_data):
    return ContextEOD(eod_data)

def test_long_position(context, buy_order):

    position = LongPosition(context, buy_order)
    assert position.side == Position.Side.LONG
    assert position.status == Position.Status.OPEN
    assert position.quantity == 1
    assert type(position.quantity) == int
    assert position.current_dollar_value == context.current_market_price("MSFT")
    assert position.order == buy_order
    assert position.have_already_been_closed == False

    position.increase(1)
    assert position.quantity == 2

    position.decrease(1)
    assert position.quantity == 1

    position.decrease(1)
    assert position.quantity == 0
    assert position.status == position.Status.CLOSED


def test_short_position(context, sell_order):

    position = ShortPosition(context, sell_order)
    assert position.side == Position.Side.SHORT
    assert position.status == Position.Status.OPEN
    assert position.quantity == 1
    assert position.current_dollar_value == -1.0 * context.current_market_price("MSFT")
    assert position.order == sell_order
    assert position.have_already_been_closed == False

    position.increase(1)
    assert position.quantity == 2

    position.decrease(1)
    assert position.quantity == 1

    position.decrease(1)
    assert position.quantity == 0
    assert position.status == position.Status.CLOSED

