
import json
import os

from ..data.daily_bar import EquityEOD
from .equity_io import save_listing
from .io_utils import *

## Don't use anything in here.

def save_eod(out_data: EquityEOD, out_dir):
    if not os.path.exists(out_dir):
        raise RuntimeError("Output directory must exist.")

    daily_bar_path = os.mkdir(os.path.join(out_dir, "daily_bar"))
    dates_path = os.mkdir(os.path.join(out_dir, "dates"))

    _save_eod_dataframes(out_data.data_frames, ohlcv_path)
    _save_eod_dates(out_data.start_date, out_data.end_date, dates_path)

def _save_eod_dataframes(out_dataframes: dict, out_dir: str):
    out_filename_template = os.path.join(out_dir, "{}.csv")

    for symbol in out_dataframes.keys():
        outfilename = out_filename_template.format(symbol)
        out_dataframes[symbol].to_csv(outfilename)

    return

def _save_eod_dates(start_date, end_date, out_dir):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    out_dict = {}
    out_dict["start_time"] = start_date_str
    out_dict["end_date"] = end_date_str

    out_filename = os.path.join(out_dir, "date_range.json")
    with open(out_filename, 'w') as outfile:
        json.dump(out_dict, outfile, indent=4)

    return

def load_eod(in_dir: str):

    if not os.path.exists(in_dir):
        raise RuntimeError("Input directory for EOD data does not exist.")

    daily_bar_path = os.path.join(in_dir, "daily_bar")
    dates_path = os.mkdir(os.path.join(out_dir, "dates"))

    if not os.path.exists(daily_bar_path) or not os.path.exists(dates_path):
        raise RuntimeError("Directory structure for eod not recognized.")
    
    filenames = sorted(glob(os.path.join(daily_bar_path, "*.csv")))

    symbols = set()
    for filename in filenames:
        symbols.add(symbol_from_filename(filename))
    
    return



