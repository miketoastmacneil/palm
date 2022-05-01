from palm.broker.simulated_broker import SimulatedBroker
from palm.data.equity_eod import EquityEOD
from palm.orders.market_order import MarketOrder, MarketOrderStatus
from palm.positions import Position
import pytest

import pandas as pd

from palm.data import polygon_symbol_indexed_to_OHCLV_indexed
from palm.context import ContextEOD


@pytest.fixture
def eod_data():

    data = {}
    data["AAPL"] = pd.read_csv("sample_data/AAPL-Sample-Data.csv", index_col=0)
    data["MSFT"] = pd.read_csv("sample_data/MSFT-Sample-Data.csv", index_col=0)

    return EquityEOD(polygon_symbol_indexed_to_OHCLV_indexed(data))


@pytest.fixture
def context(eod_data: EquityEOD):
    return ContextEOD(eod_data)


@pytest.fixture
def initial_deposit():
    return 10000


@pytest.fixture
def buy_order():
    return MarketOrder.Buy("AAPL", 10)


@pytest.fixture
def sell_order():
    return MarketOrder.Sell("AAPL", 10)


@pytest.fixture
def broker(context, initial_deposit):
    return SimulatedBroker(context, initial_deposit)

def test_broker_init(broker, initial_deposit):

    assert broker.cash_account.balance == initial_deposit
    assert broker.all_positions == {}
    assert broker.all_orders == set()

def test_SufficientBalanceBuyOrderSubmitted_OrderFulFilled(broker, buy_order):

    broker.submit_order(buy_order)
    assert buy_order.status == MarketOrderStatus.CLOSED
    assert buy_order.fulfilled == True
    assert buy_order.time_closed == broker.context.current_time()
    assert buy_order in broker.all_orders
    assert buy_order.failure_reason is None


def test_SufficientBalanceBuyOrderSubmitted_LongPositionOpened(broker, buy_order):

    broker.submit_order(buy_order)
    position = broker.get_position(buy_order.symbol)
    assert position.side == Position.Side.LONG
    assert position.status == Position.Status.OPEN
    assert (
        position.current_dollar_value
        == buy_order.quantity * broker.context.current_market_price(buy_order.symbol)
    )


def test_SufficientBalanceBuyOrderSubmitted_CashAccountDecreasedByOrderCost(
    broker, buy_order, initial_deposit
):

    broker.submit_order(buy_order)
    order_cost = buy_order.quantity * broker.context.current_market_price(
        buy_order.symbol
    )
    assert abs(broker.cash_account.balance - (initial_deposit - order_cost)) < 1.0e-5


### This should probably test if you have sufficient margin.
def test_NewSellOrderSubmitted_OrderFulfilled(broker, sell_order):
    broker.submit_order(sell_order)
    assert sell_order.status == MarketOrderStatus.CLOSED
    assert sell_order.fulfilled == True
    assert sell_order.time_closed == broker.context.current_time()
    assert sell_order in broker.all_orders
    assert sell_order.failure_reason is None
    return


def test_NewSellOrderSubmitted_ShortPositionOpened(broker, sell_order):
    broker.submit_order(sell_order)
    position = broker.get_position(sell_order.symbol)
    assert position.side == Position.Side.SHORT
    assert position.status == Position.Status.OPEN
    assert (
        position.current_dollar_value
        == -sell_order.quantity * broker.context.current_market_price(sell_order.symbol)
    )


def test_NewSellOrderSubmitted_CreditApplied(broker, sell_order, initial_deposit):

    broker.submit_order(sell_order)
    order_credit = sell_order.quantity * broker.context.current_market_price(
        sell_order.symbol
    )
    assert abs(broker.cash_account.balance - (initial_deposit + order_credit)) < 1.0e-5


def test_TwoBuyOrdersSameQuantitySubmitted_LongPositionDoubled(broker, buy_order):

    broker.submit_order(buy_order)
    new_buy = MarketOrder.Buy(buy_order.symbol, buy_order.quantity)
    broker.submit_order(new_buy)
    position = broker.get_position(buy_order.symbol)
    assert position.quantity == int(2 * buy_order.quantity)
    assert position.status == Position.Status.OPEN
    assert position.side == Position.Side.LONG


def test_BuyOrderFollowedByASellOrderSameQuantity_LongPositionClosed(
    broker, buy_order, sell_order
):

    broker.submit_order(buy_order)
    broker.submit_order(sell_order)

    pos = broker.get_position(buy_order.symbol)
    assert pos is None
    assert broker.all_positions == {}
    assert broker.portfolio_value() == broker.cash_account.balance


def test_TwoSellOrdersSameQuantitySubmitted_ShortPositionDoubled(broker, sell_order):

    broker.submit_order(sell_order)
    position = broker.get_position(sell_order.symbol)
    new_sell = MarketOrder.Sell(sell_order.symbol, sell_order.quantity)
    broker.submit_order(new_sell)
    position = broker.get_position(sell_order.symbol)
    assert position.quantity == int(2 * sell_order.quantity)
    assert position.status == Position.Status.OPEN
    assert position.side == Position.Side.SHORT


def test_BuyOrderAfterSellOrderSameQuantity_ShortPositionClosed(broker, sell_order):

    broker.submit_order(sell_order)
    position = broker.get_position(sell_order.symbol)
    assert position.quantity == sell_order.quantity
    assert position.status == Position.Status.OPEN

    new_buy = MarketOrder.Buy(sell_order.symbol, sell_order.quantity)
    broker.submit_order(new_buy)
    assert position.quantity == 0
    assert position.status == Position.Status.CLOSED

    pos = broker.get_position(sell_order.symbol)
    assert pos is None
    assert broker.all_positions == {}
    assert broker.portfolio_value() == broker.cash_account.balance
