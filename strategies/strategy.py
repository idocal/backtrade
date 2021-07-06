from enum import Enum
from dataclasses import dataclass
from candles import Candles
from typing import List, Union


class Decision(Enum):
    BUY = 1
    HOLD = 0
    SELL = -1


@dataclass
class Position:
    decision: Decision
    stop_loss: float = 0.0
    take_profit: float = 0.0
    amount: float = 0.1


class Strategy:

    def __init__(self, candles: Union[Candles, List[Candles]]):
        self.candles = candles
        self.is_multi = True if type(candles) is list and len(candles) > 1 \
            else False

    def backtest(self) -> List[Position]:
        return NotImplementedError("Strategies must implement backtest")
