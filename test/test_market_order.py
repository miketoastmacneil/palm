import pytest

import palm as pm

def test_PostiveIntegerQuantity_OrderCreated():
    order = pm.MarketOrder.Buy("MSFT", 1)

    assert order.status == pm.MarketOrderStatus.NOT_SUBMITTED
    assert order.type == pm.MarketOrderType.BUY
    assert order._quantity == 1
    assert type(order.quantity) == int
    assert order.fulfilled == False
    assert order.failure_reason == None
    assert order.avg_price == None


def test_NegativeIntegerQuantity_ValueErrorRaised():
    with pytest.raises(ValueError):
        illegal_order = pm.MarketOrder.Buy("MSFT", -1)

    with pytest.raises(ValueError):
        illegal_order = pm.MarketOrder.Sell("MSFT", -1)

def test_TwoDifferentOrdersSameSymbolSameAmount_NotEqual():

    order = pm.MarketOrder.Buy("MSFT", 1)
    second_similar_order = pm.MarketOrder.Buy("MSFT", 1)
    assert second_similar_order != order
