import pandas as pd

from ..context.daily_bar_context import ContextEOD
from ..data.yahoo_eod import YahooEOD


def ContextFromYahooEOD(src_data: pd.DataFrame):

    data = YahooEOD(src_data)

    return ContextEOD(data)
