from palm.broker.simulated_broker import SimulatedBroker
from palm.orders.market_order import MarketOrder, MarketOrderStatus
from palm.positions import Position, LongPosition, ShortPosition
import pytest

import pandas as pd

from palm.data import PolygonEOD
from palm.context import ContextEOD

@pytest.fixture
def eod_data():

    data = {}
    data["AAPL"] = pd.read_csv("sample_data/AAPL-Sample-Data.csv", index_col=0)
    data["MSFT"] = pd.read_csv("sample_data/MSFT-Sample-Data.csv", index_col=0)

    return PolygonEOD(data)

@pytest.fixture
def context(eod_data):
    return ContextEOD(eod_data)

@pytest.fixture
def initial_deposit():
    return 10000

@pytest.fixture
def buy_order():
    return MarketOrder.Buy("AAPL", 10)

@pytest.fixture
def sell_order():
    return MarketOrder.Sell("AAPL",10)

@pytest.fixture
def broker(context, initial_deposit):
    return SimulatedBroker(context, initial_deposit)    


def test_broker_init(broker, initial_deposit):

    assert broker.cash_account.balance == initial_deposit
    assert broker.all_positions == {}
    assert broker.all_orders == set()

"""
Tests a buy and sell order workflow without
updating the context.
"""
def test_submit_buy_order(broker, buy_order, initial_deposit):

    broker.submit_order(buy_order)
    assert buy_order.status == MarketOrderStatus.CLOSED
    assert buy_order.fulfilled == True
    assert buy_order.time_closed == broker.context.current_time()
    assert buy_order in broker.all_orders
    assert buy_order.failure_reason is None
    assert abs(buy_order.avg_cost - broker.context.current_market_price(buy_order.symbol)) < 1.0e-5 

    position = broker.get_position(buy_order.symbol)
    assert position.side == Position.Side.LONG
    assert position.status == Position.Status.OPEN

    order_cost = buy_order.quantity * broker.context.current_market_price(buy_order.symbol)
    assert abs(broker.cash_account.balance - (initial_deposit - order_cost)) < 1.0e-5


def test_submit_sell_order(broker, sell_order, initial_deposit):

    broker.submit_order(sell_order)
    assert sell_order.status == MarketOrderStatus.CLOSED
    assert sell_order.fulfilled == True
    assert sell_order.time_closed == broker.context.current_time()
    assert sell_order in broker.all_orders
    assert sell_order.failure_reason is None
    assert abs(sell_order.avg_cost - broker.context.current_market_price(sell_order.symbol)) < 1.0e-5 

    position = broker.get_position(sell_order.symbol)
    assert position.side == Position.Side.SHORT
    assert position.status == Position.Status.OPEN

    order_cost = sell_order.quantity * broker.context.current_market_price(buy_order.symbol)
    assert abs(broker.cash_account.balance - (initial_deposit + order_credit)) < 1.0e-5
 
    