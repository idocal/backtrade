from indicators.indicator import Indicator
import numpy as np
from talib import stream


class SMA(Indicator):

    def __init__(self, period, param='Close'):
        assert param in ['Open', 'High', 'Low', 'Close', 'Volume']
        self.period = period
        self.param = param
        self.values = np.array([], dtype='float64')

    @property
    def name(self):
        return f'{self.period} SMA'

    def next(self, candle):
        value = candle.__dict__[self.param.lower()]
        self.values = np.append(self.values, value)
        return stream.SMA(self.values, timeperiod=self.period)
