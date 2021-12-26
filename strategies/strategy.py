from enum import Enum
from candles import Candle


class Decision(Enum):
    HOLD = 0
    LONG = 1
    SHORT = 2
    PULL = 3
    STOPLOSS = 4
    TAKE_PROFIT = 5

    def __str__(self):
        d = {
            0: 'hold',
            1: 'long',
            2: 'short',
            3: 'pull',
            4: 'stoploss',
            5: 'take profit'
        }
        return d[self.value]


class Strategy:

    def __init__(self):
        self.stoploss = None
        self.take_profit = None

    def set_stoploss(self, stoploss: float):
        self.stoploss = stoploss

    def set_take_profit(self, take_profit: float):
        self.take_profit = take_profit

    def _next(self, candle: Candle) -> Decision:
        decision = None
        sl_condition = self.stoploss is not None \
            and candle.close <= self.stoploss
        tp_condition = self.take_profit is not None \
            and candle.close >= self.take_profit

        if sl_condition:
            decision = Decision.STOPLOSS
        elif tp_condition:
            decision = Decision.TAKE_PROFIT

        return decision

    def process(self, candle: Candle) -> Decision:
        preprocess = self._next(candle)
        decision = self.next(candle)
        if preprocess is not None:
            return preprocess
        return decision

    def next(self, candle: Candle) -> Decision:
        return NotImplementedError("Strategies must implement next")
