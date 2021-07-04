import pandas as pd
import numpy as np
from indicator import SMA
from enum import Enum
from dataclasses import dataclass
from candles import Candles


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

    def __init__(self, data: Candles):
        self.data = data

    def backtest(self) -> np.ndarray:
        return NotImplementedError("Strategies must implement backtest")


class SMACrossover(Strategy):

    def __init__(self, data, small=50, large=200):
        super().__init__(data)
        self.small = small
        self.large = large

    def backtest(self):
        small_sma = SMA(data=self.data, window=self.small)
        small_sma_values = small_sma.indicator()
        large_sma = SMA(data=self.data, window=self.large)
        large_sma_values = large_sma.indicator()

        positions = []
        is_small_higher = True
        for i in range(1, len(large_sma_values)):
            is_current_small_higher = small_sma_values[i] > large_sma_values[i]
            if is_current_small_higher != is_small_higher:
                trend = small_sma_values[i] - small_sma_values[i-1]
                if trend > 0:
                    position = Position(decision=Decision.SELL)
                else:
                    position = Position(decision=Decision.BUY)
                is_small_higher = is_current_small_higher
            else:
                position = Position(decision=Decision.HOLD)

            positions.append(position)

        return positions
