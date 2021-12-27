from strategies.strategy import Strategy, Decision
from indicators.SMA import SMA


class SMACrossover(Strategy):

    def __init__(self, small=50, large=200):
        super().__init__()
        self.small = small
        self.large = large
        # initialize indicators
        self.small_sma = SMA(period=self.small)
        self.large_sma = SMA(period=self.large)
        self.is_small_higher = True

        self.small_sma_prev = float('nan')

    def next(self, candle):
        factor = 2
        margin = 0.02
        small_sma = self.small_sma(candle)
        large_sma = self.large_sma(candle)
        small_sma_prev = self.small_sma_prev

        is_current_small_higher = small_sma > large_sma

        # strategy holds by default
        decision = Decision.HOLD

        # detect a crossover
        if is_current_small_higher != self.is_small_higher:
            trend = small_sma - small_sma_prev
            close = candle.close
            # if small sma is trending up, place a short
            if trend > 0:
                stoploss = (1 + margin / factor) * close
                take_profit = (1 - margin) * close
                decision = Decision.SHORT
            else:
                # if small sma is trending down, place a long
                stoploss = (1 - margin / factor) * close
                take_profit = (1 + margin) * close
                decision = Decision.LONG

            self.set_stoploss(stoploss)
            self.set_take_profit(take_profit)
            self.is_small_higher = is_current_small_higher

        self.small_sma_prev = small_sma

        return decision
