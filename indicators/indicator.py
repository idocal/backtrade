from candles import Candle


class Indicator:

    @property
    def name(self):
        return 'Indicator'

    def next(self, candle):
        raise NotImplementedError()

    def __call__(self, candle: Candle):
        return self.next(candle)
