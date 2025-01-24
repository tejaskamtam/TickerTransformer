# Tokenizes stock data into json format

from enum import Enum
import os
import requests
import pandas as pd
import numpy as np
import dotenv

class API(Enum):
    # only twelvedata is supported currently
    TWELVEDATA = 1
    # POLYGON = 2
    # ALPHAVANTAGE = 3

class INTERVAL(Enum):
    # unique to twelvedata: 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day, 1week, 1month
    MINUTE = "1min"
    FIVE_MINUTE = "5min"
    FIFTEEN_MINUTE = "15min"
    THIRTY_MINUTE = "30min"
    FOURTY_FIVE_MINUTE = "45min"
    HOUR = "1h"
    TWO_HOUR = "2h"
    FOUR_HOUR = "4h"
    DAY = "1day"
    WEEK = "1week"
    MONTH = "1month"

class TickerTokenizer:
    def __init__(self, api=API.TWELVEDATA, api_key=None):
        self.api_key = api_key
        self.api = api

    def tokenize(self, ticker: str, interval: INTERVAL = INTERVAL.DAY, num_ticks: int = 5000) -> pd.DataFrame:
        # adds calculated fields: log_returns, volume_change, volume_change_pct
        if self.api == API.TWELVEDATA:
            return self._tokenize_twelvedata(ticker, interval.value, num_ticks)
        else:
            raise ValueError(f"API {self.api} not supported")

    def _tokenize_twelvedata(self, ticker: str, interval: str, num_ticks: int = 5000) -> pd.DataFrame:
        ### format of series[i]
        # {
        #     "datetime": "2025-01-21",
        #     "open": "600.66998",
        #     "high": "603.059998",
        #     "low": "598.67999",
        #     "close": "603.049988",
        #     "volume": "35470766"
        # }

        # fetch data from api
        url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval={interval}&outputsize={num_ticks}&apikey={self.api_key}"
        response: dict[str, any] = requests.get(url).json()
        series: list[dict[str, any]] = response["values"]

        # convert to dataframe
        df = pd.DataFrame(series)

        # add calculated fields
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["volume"] = df["volume"].astype(float)
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)

        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))
        df["volume_change"] = df["volume"] - df["volume"].shift(1)
        df["volume_change_pct"] = df["volume_change"] / df["volume"].shift(1)

        # replace nan with 0
        df = df.fillna(0)

        return df
