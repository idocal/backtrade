from enum import Enum
from dataclasses import dataclass
from candles import Candles, Candle
from typing import List, Union
from datetime import datetime


class Decision(Enum):
    HOLD = 0
    LONG = 1
    SHORT = 2
    PULL = 3


class Side(Enum):
    LONG = 1
    SHORT = -1


@dataclass
class Trade:
    stoploss: float
    take_profit: float
    date: datetime
    side: Side = Side.LONG
    is_profitable = None

    def __repr__(self):
        return f"{'LONG' if self.side == Side.LONG else 'SHORT'}(\
            stoploss: {self.stoploss:.4f} take_profit: {self.take_profit:.4f})"


class Strategy:

    def __init__(self, candles: Union[Candles, List[Candles]] = None):
        self.candles = candles
        self.is_multi = True if type(candles) is list and len(candles) > 1 \
            else False
        self.stoploss = None
        self.take_profit = None

    def set_stoploss(self, stoploss: float):
        self.stoploss = stoploss

    def set_take_profit(self, take_profit: float):
        self.take_profit = take_profit

    def _next(self, candle: Candle) -> Decision:
        decision = None
        sl_condition = self.stoploss and candle.close <= self.stoploss
        tp_condition = self.take_profit and candle.close >= self.take_profit

        if sl_condition or tp_condition:
            decision = Decision.PULL
            self.set_stoploss(None)
            self.set_take_profit(None)

        return decision

    def process(self, candle: Candle) -> Decision:
        preprocess = self._next(candle)
        decision = self.next(candle)
        return preprocess if preprocess else decision

    def next(self, candle: Candle) -> Decision:
        return NotImplementedError("Strategies must implement next")

    def backtest(self) -> List[Trade]:
        return NotImplementedError("Strategies must implement backtest")
