import pytest

from palm.orders import MarketOrder, MarketOrderStatus, MarketOrderType

def test_PostiveIntegerQuantity_OrderCreated():
    order = MarketOrder.Buy("MSFT", 1)

    assert order.status == MarketOrderStatus.NOT_SUBMITTED
    assert order.type == MarketOrderType.BUY
    assert order._quantity == 1
    assert type(order.quantity) == int
    assert order.fulfilled == False
    assert order.failure_reason == None
    assert order.avg_price == None

def test_NegativeIntegerQuantity_ValueErrorRaised():
    with pytest.raises(ValueError):
        illegal_order = MarketOrder.Buy("MSFT", -1)

    with pytest.raises(ValueError):
        illegal_order = MarketOrder.Sell("MSFT", -1)

def test_TwoDifferentOrdersSameSymbolSameAmount_NotEqual():

    order = MarketOrder.Buy("MSFT",1)
    second_similar_order = MarketOrder.Buy("MSFT",1)
    assert second_similar_order != order 
    