import pytest

from palm.orders import MarketOrder, MarketOrderStatus, MarketOrderType

def test_legal_init():
    order = MarketOrder.Buy("MSFT", 1)

    assert order.status == MarketOrderStatus.NOT_SUBMITTED
    assert order.type == MarketOrderType.BUY
    assert order._quantity == 1
    assert order.fulfilled == False
    assert order.position_id == None

def test_illegal_init():
    with pytest.raises(ValueError):
        illegal_order = MarketOrder.Buy("MSFT", -1)

    with pytest.raises(ValueError):
        illegal_order = MarketOrder.Sell("MSFT", -1)


    
    