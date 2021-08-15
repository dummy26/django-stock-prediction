from ..data.constants import SYMBOL_COLUMN
from ..data.utils import get_all_nse_company_names_and_ticker


class InvalidTickerError(Exception):
    def __init__(self, ticker: str) -> None:
        msg = f"'{ticker}' is not a valid stock ticker"
        super().__init__(msg)


def validate_ticker(ticker):
    df = get_all_nse_company_names_and_ticker()

    df = df[df[SYMBOL_COLUMN].str.fullmatch(ticker, case=False)]
    if len(df) <= 0:
        raise InvalidTickerError(ticker)
