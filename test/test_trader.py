import pytest

import pandas as pd

from palm.data import EquityEOD, polygon_symbol_indexed_to_OHCLV_indexed
from palm.context import ContextEOD, TimeInMarketDay
from palm.trader import SimulatedTrader

from palm.trades import Trade


@pytest.fixture
def eod_data():

    data = {}
    data["AAPL"] = pd.read_csv("sample_data/AAPL-Sample-Data.csv", index_col=0)
    data["MSFT"] = pd.read_csv("sample_data/MSFT-Sample-Data.csv", index_col=0)

    return EquityEOD(polygon_symbol_indexed_to_OHCLV_indexed(data))


@pytest.fixture
def context(eod_data):
    return ContextEOD(eod_data)


def test_OnConstruction_NoActiveOrClosedTrades(context):
    initial_deposit = 10000

    trader = SimulatedTrader(context, initial_deposit)

    assert len(trader.open_trades) == 0
    assert len(trader.closed_trades) == 0


def test_one_update_workflow(context):

    initial_deposit = 10000
    trader = SimulatedTrader(context, initial_deposit)

    assert len(trader.open_trades) == 0
    assert len(trader.closed_trades) == 0

    class ExitRule:
        def __init__(self, context, time_to_close):
            self.context = context
            self.time_to_close = time_to_close

        def __call__(self):
            is_closing = self.context.time_in_market_day() == TimeInMarketDay.Closing
            is_next_day = self.context.current_date_index() == self.time_to_close
            return is_closing and is_next_day

    exit_rule = ExitRule(context, 1)
    trade = Trade({"AAPL": 1, "MSFT": -1}, exit_rule)
    trader.submit_trade(trade)

    context.update()
    context.update()
    context.update()

    assert trade.exit_rule_triggered()
    assert trade.status == Trade.Status.COMPLETE
    assert trader.broker.all_positions == {}
    assert len(trader.broker.all_orders) == 4

    ## TODO: Need to ensure there was
    ## 4 orders submitted.
    ## They all are closed, and were all fullfilled.
