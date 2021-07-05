from indicators.indicator import Indicator
import numpy as np
import talib


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

    def indicator(self) -> np.ndarray:
        data = self.candles.data[self.param].to_numpy()
        return talib.SMA(data, timeperiod=self.period)
