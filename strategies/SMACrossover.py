from strategies.strategy import Strategy, Position, Decision
from indicators.SMA import SMA


class SMACrossover(Strategy):

    def __init__(self, candles, small=50, large=200):
        super().__init__(candles)
        self.small = small
        self.large = large

    def backtest(self):
        small_sma = SMA(candles=self.candles, period=self.small)
        small_sma_values = small_sma.indicator()
        large_sma = SMA(candles=self.candles, period=self.large)
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
