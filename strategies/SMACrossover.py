from strategies.strategy import Strategy, Trade, Side, Decision
from indicators.SMA import SMA


class SMACrossover(Strategy):

    def __init__(self, candles, small=50, large=200):
        super().__init__(candles)
        self.small = small
        self.large = large

        # initialize indicators
        small_sma = SMA(candles=self.candles, period=self.small)
        self.small_sma = small_sma.indicator()
        large_sma = SMA(candles=self.candles, period=self.large)
        self.large_sma = large_sma.indicator()
        self.counter = 1
        self.is_small_higher = True

    def backtest(self):
        small_sma = SMA(candles=self.candles, period=self.small)
        small_sma_values = small_sma.indicator()
        large_sma = SMA(candles=self.candles, period=self.large)
        large_sma_values = large_sma.indicator()

        trades = [None]
        is_small_higher = True
        factor = 2
        margin = 0.02

        for i in range(1, len(large_sma_values)):
            trade = None
            date = self.candles.data.index[i]
            is_current_small_higher = small_sma_values[i] > large_sma_values[i]
            # detect a crossover
            if is_current_small_higher != is_small_higher:
                trend = small_sma_values[i] - small_sma_values[i-1]
                close = self.candles.close[i]
                # if small sma is trending up, place a short
                if trend > 0:
                    side = Side.SHORT
                    stoploss = (1 + margin / factor) * close
                    take_profit = (1 - margin) * close
                    trade = Trade(stoploss, take_profit, date, side)
                else:
                    # if small sma is trending down, place a long
                    side = Side.LONG
                    stoploss = (1 - margin / factor) * close
                    take_profit = (1 + margin) * close
                    trade = Trade(stoploss, take_profit, date, side)
                is_small_higher = is_current_small_higher

            trades.append(trade)

        return trades

    def next(self, candle):
        factor = 2
        margin = 0.02
        i = self.counter
        is_current_small_higher = self.small_sma[i] > self.large_sma[i]

        # detect a crossover
        if is_current_small_higher != self.is_small_higher:
            trend = self.small_sma[i] - self.small_sma[i-1]
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

        self.counter += 1
        return decision
