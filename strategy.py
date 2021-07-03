import pandas as pd
import numpy as np
from indicator import SMA
from enum import Enum
from dataclasses import dataclass


class Decision(Enum):
    BUY = 1
    HOLD = 0
    SELL = -1


@dataclass
class Position:
    stop_loss: float
    take_profit: float


class Strategy:

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def decision(self) -> np.ndarray:
        return NotImplementedError("Strategies must implement decision")


class SMACrossover(Strategy):

    def __init__(self, data, small=10, big=30):
        super().__init__(data)
        self.small = small
        self.big = big

    def decision(self):
        small_sma = SMA(data=self.data, window=self.small)
        big_sma = SMA(data=self.data, window=self.big)
        
