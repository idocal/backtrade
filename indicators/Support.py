from indicators.indicator import Indicator
import numpy as np


class Support(Indicator):

    def __init__(self, candles, period):
        super().__init__(candles)
        self.num_ticks = len(candles)
        assert period <= self.num_ticks
        self.period = period

    @property
    def name(self):
        return f'{self.period} Support'

    def indicator(self) -> np.ndarray:
        ret = np.zeros(len(self.candles))
        lows = self.candles.low
        for i in range(self.period, len(self.candles)):
            ret[i] = np.min(lows[i-self.period:i])
        ret[:self.period] = np.nan
        return ret
