from sqlite3 import Time
from palm import data
from palm.context.daily_bar_context import ContextEOD, TimeInMarketDay
import pytest

import pandas as pd
from palm.data import EquityEOD, polygon_symbol_indexed_to_OHCLV_indexed


@pytest.fixture
def eod_data():

    data = {}
    data["AAPL"] = pd.read_csv("sample_data/AAPL-Sample-Data.csv", index_col=0)
    data["MSFT"] = pd.read_csv("sample_data/MSFT-Sample-Data.csv", index_col=0)

    return EquityEOD(polygon_symbol_indexed_to_OHCLV_indexed(data))


def test_init(eod_data):
    context = ContextEOD(eod_data)
    assert context.current_date_index() == 0
    assert context.time_in_market_day() == TimeInMarketDay.Opening
    assert context._max_date_index == 177
    assert context.can_still_update()
    assert context.observers == {}


def test_InitWithStartDateOneDayAfterFirst_DateIndexIsOne(eod_data):
    context = ContextEOD(eod_data)
    assert context.current_date_index() == 0


def test_OneTimeStep_MovesFromOpeningToClosing(eod_data):

    context = ContextEOD(eod_data)
    assert context.current_date_index() == 0
    assert context.time_in_market_day() == TimeInMarketDay.Opening
    assert context.can_still_update()

    context.update()

    assert context.current_date_index() == 0
    assert context.time_in_market_day() == TimeInMarketDay.Closing
    assert context.can_still_update()


def test_AtFinalTimeStep_CanUpdateIsFalse(eod_data):
    context = ContextEOD(eod_data)
    second_last_date = context._max_date_index - 1
    for i in range(second_last_date * 2):
        context.update()

    context.update()  ## move to closing.
    context.update()  ## move to final day opening
    context.update()  ## Move to close
    assert context.can_still_update() == False


def test_MarketPricesInFirstTwoSteps_GivesOpenThenClose(eod_data):

    context = ContextEOD(eod_data)

    ## Prices taken from opening.
    assert context.current_market_price("AAPL") == 79.2975
    assert context.current_market_price("MSFT") == 166.68

    context.update()

    ## Prices taken from first day close.
    assert context.current_market_price("AAPL") == 79.1425
    assert context.current_market_price("MSFT") == 166.5


def test_FirstTenSteps_GiveCorrectMarketPricesForEach(eod_data):

    context = ContextEOD(eod_data)
    first_aapl_open_prices = [
        79.2975,
        79.645,
        79.48,
        80.0625,
        77.515,
        78.15,
        81.1125,
        80.1359,
        80.2325,
        76.075,
    ]
    first_aapl_close_prices = [
        79.1425,
        79.425,
        79.8075,
        79.5775,
        77.2375,
        79.4225,
        81.085,
        80.9675,
        77.3775,
        77.165,
    ]

    first_msft_open_prices = [
        166.68,
        167.4,
        166.19,
        167.51,
        161.15,
        163.78,
        167.84,
        174.05,
        172.21,
        170.43,
    ]
    first_msft_close_prices = [
        166.5,
        165.7,
        166.72,
        165.04,
        162.28,
        165.46,
        168.04,
        172.78,
        170.23,
        174.38,
    ]

    ## Only evaluate the first ten
    for i, event in enumerate(context):
        if i > 10:
            break
        else:
            assert event.date_index_since_start == i // 2
            if i % 2 == 0:
                assert event.time_in_market_day == TimeInMarketDay.Opening
                assert (
                    context.current_market_price("AAPL")
                    == first_aapl_open_prices[i // 2]
                )
                assert (
                    context.current_market_price("MSFT")
                    == first_msft_open_prices[i // 2]
                )
            else:
                assert event.time_in_market_day == TimeInMarketDay.Closing
                assert (
                    context.current_market_price("AAPL")
                    == first_aapl_close_prices[i // 2]
                )
                assert (
                    context.current_market_price("MSFT")
                    == first_msft_close_prices[i // 2]
                )
            assert event.date_index_since_start == context.current_date_index()
            assert event.time_in_market_day == context.time_in_market_day()
