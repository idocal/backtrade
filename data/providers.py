from __future__ import annotations

import urllib.error
from abc import abstractmethod
from typing import Literal
import pandas as pd
import datetime
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import loguru

VALID_PROVIDERS = Literal["Binance", "binance"]

# TODO:
#      - allow valid intervals and symbols per provider,
#      - allow multiple assets

VALID_INTERVALS = Literal["1m", "5m", "15m", "1h", "4h", "1d"]
VALID_SYMBOLS = {"BTC", "ETH", "ETC", "BNB", "XRP", "LTC"}


def get_provider(provider: str, logger: loguru.Logger):
    if provider.lower() == "binance":
        return Binance(logger)


class DownloadError(Exception):
    pass


class DataProvider:
    """
    Defines a data provider
    """

    def __init__(self, name: str, logger: loguru.Logger = None):
        self.name = name
        self.logger = logger

    @abstractmethod
    def retrieve_data(
        self, symbol: str, interval: str, year: str, month: str
    ) -> pd.DataFrame:
        pass


class Binance(DataProvider):
    def __init__(self, logger: loguru.Logger = None):
        super().__init__("Binance", logger)
        self.base_url = "https://data.binance.vision/data/spot/monthly/klines"

    def retrieve_data(self, symbol: str, interval: str, year: str, month: str):
        filename = f"{symbol}-{interval}-{year}-{month}"
        url = f"{self.base_url}/{symbol}/{interval}/{filename}.zip"

        csv_filename = f"{filename}.csv"
        if self.logger:
            self.logger.info(f"Reading from url: {url}")
        try:
            resp = urlopen(url)
        except urllib.error.HTTPError:
            raise DownloadError(f"Couldn't fetch data from {self.name} at {url}")

        zf = ZipFile(BytesIO(resp.read()))

        # read csv file in zip
        df = pd.read_csv(zf.open(csv_filename), header=None)
        df.drop(df.columns[6:], axis=1, inplace=True)
        df.columns = ["Timestamp", "Open", "High", "Low", "Close", "Volume"]

        # convert unix timestamp to datetime
        df["Timestamp"] = df["Timestamp"].apply(
            lambda t: datetime.datetime.utcfromtimestamp(t / 1000)
        )

        return df
