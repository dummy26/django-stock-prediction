import os
from functools import lru_cache

import pandas as pd
from model_backend.data.constants import (NAME_OF_COMP_COLUMN, SYMBOL_COLUMN,
                                          TICKERS_CSV)


@lru_cache(maxsize=1)
def get_all_nse_company_names_and_ticker() -> pd.DataFrame:
    dirname = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dirname, TICKERS_CSV)

    df = pd.read_csv(file_path)
    df = df[[NAME_OF_COMP_COLUMN, SYMBOL_COLUMN]]
    return df
