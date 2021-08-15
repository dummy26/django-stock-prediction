import pandas as pd

from .constants import NAME_OF_COMP_COLUMN, SYMBOL_COLUMN


def get_all_nse_company_names_and_ticker() -> pd.DataFrame:
    url = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'
    df = pd.read_csv(url)
    df = df[[NAME_OF_COMP_COLUMN, SYMBOL_COLUMN]]
    return df
