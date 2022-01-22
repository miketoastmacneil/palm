
from sqlite3 import Time
from palm import data
from palm.context.daily_bar_context import ContextEOD, TimeInMarketDay
import pytest 

import pandas as pd
from palm.data import PolygonEOD

@pytest.fixture
def eod_data():

    data = {}
    data["AAPL"] = pd.read_csv("sample_data/AAPL-Sample-Data.csv", index_col=0)
    data["MSFT"] = pd.read_csv("sample_data/MSFT-Sample-Data.csv", index_col=0)

    return PolygonEOD(data)

def test_init(eod_data):
    context = ContextEOD(eod_data)
    assert context.current_date_index()==0
    assert context.time_in_market_day()==TimeInMarketDay.Opening
    assert context._max_date_index==177
    assert context.can_still_update()
    assert context.observers == {}

def test_one_time_step(eod_data):

    context = ContextEOD(eod_data)
    context.update()

    assert context.current_date_index()==0
    assert context.time_in_market_day()==TimeInMarketDay.Closing
    assert context.can_still_update()

    context.update()

    assert context.current_date_index()==1
    assert context.time_in_market_day()==TimeInMarketDay.Opening
    assert context.can_still_update()

def test_final_time_step(eod_data):
    context = ContextEOD(eod_data)
    second_last_date = context._max_date_index-1
    for i in range(second_last_date*2):
        context.update()

    assert context.can_still_update()
    assert context.time_in_market_day()==TimeInMarketDay.Opening
    assert context.current_date_index()==second_last_date

    context.update() ## move to closing.
    context.update() ## move to final day opening
    assert context.current_date_index() == context._max_date_index
    context.update() ## Move to close
    assert context.can_still_update()==False

## TODO: Test iterator and subscribable.

def test_market_price(eod_data):

    context = ContextEOD(eod_data)

    ## Prices taken from opening.
    assert context.current_market_price("AAPL") == 79.2975
    assert context.current_market_price("MSFT") == 166.68

    context.update()

    ## Prices taken from first day close.
    assert context.current_market_price("AAPL") == 79.1425
    assert context.current_market_price("MSFT") == 166.5

def test_iterator(eod_data):

    context = ContextEOD(eod_data)

    ## Only evaluate the first ten
    for i, event in enumerate(context):
        if i > 10:
            break
        else:
            assert event.date_index_since_start == i//2 
            if i % 2 == 0:
                assert event.time_in_market_day == TimeInMarketDay.Opening
            else:
                assert event.time_in_market_day == TimeInMarketDay.Closing  
            assert event.date_index_since_start == context.current_date_index()
            assert event.time_in_market_day == context.time_in_market_day()
    
## TODO test an observer.