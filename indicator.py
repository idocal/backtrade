import numpy as np
import pandas as pd
from candles import Candles


class Indicator:

    def __init__(self, data: Candles):
        self.data = data

    def indicator(self) -> pd.DataFrame:
        raise NotImplementedError()

    @property
    def name(self):
        return 'Indicator'


class SMA(Indicator):

    def __init__(self, data, window, param='Close'):
        super().__init__(data)
        self.num_ticks = len(data)
        assert window <= self.num_ticks
        self.window = window
        self.param = param

    @property
    def name(self):
        return f'{self.window} SMA'

    @staticmethod
    def rolling_mean(x: pd.DataFrame, window):
        return x.rolling(window=window).mean()[window-1:]

    def indicator(self) -> np.ndarray:
        sma = self.rolling_mean(self.data.data, self.window)
        return sma[self.param].to_numpy()
