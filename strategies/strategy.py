from enum import Enum
from dataclasses import dataclass
from candles import Candles
from typing import List, Union
from datetime import datetime


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
        return f"{'LONG' if self.side == Side.LONG else 'SHORT'}\
            (stoploss: {self.stoploss:.4f} take_profit: {self.take_profit:.4f})"


class Strategy:

    def __init__(self, candles: Union[Candles, List[Candles]]):
        self.candles = candles
        self.is_multi = True if type(candles) is list and len(candles) > 1 \
            else False

    def backtest(self) -> List[Trade]:
        return NotImplementedError("Strategies must implement backtest")
