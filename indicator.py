import numpy as np
import pandas as pd
from candles import Candles
import talib


class Indicator:

    def __init__(self, candles: Candles):
        self.candles = candles

    @property
    def name(self):
        return 'Indicator'

    def indicator(self) -> np.ndarray:
        raise NotImplementedError()


class SMA(Indicator):

    def __init__(self, candles, period, param='Close'):
        super().__init__(candles)
        self.num_ticks = len(candles)
        assert period <= self.num_ticks
        assert param in ['Open', 'High', 'Low', 'Close', 'Volume']
        self.period = period
        self.param = param

    @property
    def name(self):
        return f'{self.period} SMA'

    @staticmethod
    def rolling_mean(x: pd.DataFrame, period):
        return x.rolling(window=period).mean()[period-1:]

    def indicator(self) -> np.ndarray:
        data = self.candles.data[self.param].to_numpy()
        return talib.SMA(data, timeperiod=self.period)
