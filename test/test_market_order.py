import pytest

from palm.orders.market_order import MarketOrder, MarketOrderStatus, MarketOrderType

def test_market_order_init():
    ## Fair initialization
    order = MarketOrder.Buy("MSFT", 1)

    assert order.status == MarketOrderStatus.NOT_SUBMITTED
    assert order.type == MarketOrderType.BUY
    assert order._quantity == 1
    assert order.fulfilled == False
    assert order.position_id == None

def test_illegal_init():
    with pytest.raises(ValueError):
        illegal_order = MarketOrder.Buy("MSFT", -1)


def test_submission():

    order = MarketOrder.Buy("MSFT", 1)


    
    