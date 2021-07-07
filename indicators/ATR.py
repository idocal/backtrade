from indicators.indicator import Indicator
import numpy as np
import talib


class ATR(Indicator):

    def __init__(self, candles, period):
        super().__init__(candles)
        self.num_ticks = len(candles)
        assert period <= self.num_ticks
        self.period = period

    @property
    def name(self):
        return f'{self.period} ATR'

    def indicator(self) -> np.ndarray:
        high = self.candles.high.to_numpy()
        low = self.candles.low.to_numpy()
        close = self.candles.close.to_numpy()
        return talib.ATR(high, low, close, timeperiod=self.period)
