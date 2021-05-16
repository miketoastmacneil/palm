
from datetime import datetime
import pprint


class PolygonEquity:

    """
    Encapsulates Equity details as listed in the Polygon io docs.
    A list of fields is given here: 
    https://polygon.io/docs/#get_v1_meta_symbols__symbol__company_anchor,
    be repeated below for convenience. The only fields we alter
    from the polygon docs are 'listdate' and `updated'. 
    
    Example
    -------

    Fields
    ------
    logo: string
        - URL of entities logo.
    exchange: string
        - Symbols primary exchange.
    name: string
        - Name of the company / entity.
    symbol: string
        - Actual exchange symbol this item is traded under.
    listdate: datetime
        - Date this symbol was listed on the exchange.
    cik: string
        - Official CIK guid used for SEC database / filings.
    bloomberg: string
        - Bloomberg guid for this symbol.
    figi: string
        - guid for the OpenFigi project ( https://openfigi.com/ ).
    lei: string
        - Legal Entity Identifier (LEI) guid for symbol ( https://en.wikipedia.org/wiki/Legal_Entity_Identifier ).
    sic: integer
        - Standard Industrial Classification (SIC) id for symbol ( https://en.wikipedia.org/wiki/Standard_Industrial_Classification )
    country: string
        - Country in which this company is registered.
    industry: string
        - Industry this company operates in.
    sector: string
        - Sector of the indsutry in which this symbol operates in.
    marketcap: integer
        - Current market cap for this company.
    employees: integer
        - Approximate number of employees
    phone: string
        - Phone number for this company. Usually corporate contact number.
    ceo: string
        - Name of the companies current CEO.
    url: string
        - URL of the companies website.
    description: string
        - A description of the company and what they do/offer.
    similar: list[str]
    tags: list[str]
    updated: string
        - Last time this company record was updated.
    """

    def __init__(self, raw_dict: dict):

        if "_raw" not in raw_dict.keys():
            raise RuntimeError("Polygon equity constructor needs a dictionary with '_raw' as the only key.")
        self.__dict__ = raw_dict["_raw"]

        ## Convert dates to datetime
        self.listdate = datetime.strptime(self.listdate, '%Y-%m-%d') if self.listdate is not None else None
        self.updated  = datetime.strptime(self.updated, '%m/%d/%Y') if self.updated is not None else None

    def __repr__(self):
        pp = pprint.PrettyPrinter(indent = 4)
        return pp.pformat(self.__dict__)

