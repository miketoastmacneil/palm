import json
import os
from glob import glob

from .io_utils import *
from ..asset.equity import PolygonEquity

"""
Helper functions for loading or saving the PolygonEquity class.
"""


def save_listings(listings: list, output_dir: str):
    """
    Save a list of PolygonEquity objects (listings) to
    a specified output directory. Each listing is written
    to its own json file.

    Parameters
    ----------
    listings: list[PolygonEquity] list of equity objects
    output_dir: output directory.

    Returns
    -------
    None
    """

    if not os.path.exists(output_dir):
        raise RuntimeError("Output directory for listings does not exist.")

    output_filename_template = os.path.join(output_dir, "{}.json")

    for listing in listings:
        output_filename = output_filename_template.format(listing.symbol)
        save_listing(listing, output_filename)

    return


def save_listing(equity_listing: PolygonEquity, outfile_name: str):
    out_dict = dict(equity_listing.__dict__)

    ## Converts these dates to match whats in Polygon (see PolygonEquity)
    out_dict["listdate"] = (
        equity_listing.listdate.strftime("%Y-%m-%d")
        if equity_listing.listdate is not None
        else None
    )
    out_dict["updated"] = (
        equity_listing.updated.strftime("%m/%d/%Y")
        if equity_listing.updated is not None
        else None
    )

    other = {}
    other["_raw"] = out_dict

    with open(outfile_name, "w") as outfile:
        json.dump(other, outfile, indent=4)

    return


def load_listings(listing_dir: str, symbols: list = None, get_all=False):
    """
    Load a set of listings, specified by symbols, from
    a directory containing listings written to a json file.

    Parameters
    ----------
    listing_dir: input directory, listings are assumed to have names <symbol>.json
    symbols: List of symbols to load.

    Returns
    -------
    listings: list[PolygonEquity]
    """

    all_listings = sorted(glob(os.path.join(listing_dir, "*.json")))

    if symbols is not None:
        symbols_set = set(symbols)
    listings = []

    if (get_all is False) and (symbols is None):
        raise RuntimeError("Need to select at least one symbol")

    for listing_filename in all_listings:
        listing_filename_symbol = symbol_from_filename(listing_filename)
        if get_all:
            listings.append(load_listing(listing_filename))
            continue
        elif listing_filename_symbol in symbols_set:
            listings.append(load_listing(listing_filename))

    return listings


def load_listing(listing_json_file: str):

    if not listing_json_file.endswith(".json"):
        raise RuntimeError("load_listing expects a json file")

    with open(listing_json_file, "r") as infile:
        raw_dict = json.load(infile)

    return PolygonEquity(raw_dict)
