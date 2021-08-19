from indicators.indicator import Indicator
import numpy as np
from talib import stream


class ATR(Indicator):

    def __init__(self, period):
        self.period = period
        self.high = np.array([], dtype='float64')
        self.low = np.array([], dtype='float64')
        self.close = np.array([], dtype='float64')

    @property
    def name(self):
        return f'{self.period} ATR'

    def next(self, candle):
        self.high = np.append(self.high, candle.high)
        self.low = np.append(self.low, candle.low)
        self.close = np.append(self.close, candle.close)
        return stream.ATR(self.high, self.low, self.close,
                          timeperiod=self.period)
