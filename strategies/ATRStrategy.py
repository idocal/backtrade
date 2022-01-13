from strategies.strategy import Strategy
from indicators.SMA import SMA
from indicators.RSI import RSI
from indicators.ATR import ATR
from strategies.strategy import Decision


class ATRStrategy(Strategy):

    def __init__(self):
        super().__init__()
        # indicators
        self.sma = SMA(period=360, param='Close')
        self.atr_last = ATR(period=5)
        self.atr_all = ATR(period=10)
        self.atr = ATR(period=14)
        self.rsi_last = RSI(period=5, param='Close')
        self.rsi_mid = RSI(period=20, param='Close')
        self.rsi_all = RSI(period=100, param='Close')

        # prev step values
        self.rsi_last_prev = float('nan')
        self.rsi_mid_prev = float('nan')
        self.rsi_all_prev = float('nan')

    def next(self, candle) -> Decision:
        # calculate indicators
        sma = self.sma(candle)
        atr_last = self.atr_last(candle)
        atr_all = self.atr_all(candle)
        atr = self.atr(candle)
        rsi_last = self.rsi_last(candle)
        rsi_mid = self.rsi_mid(candle)
        rsi_all = self.rsi_all(candle)
        rsi_prev = self.rsi_last_prev + self.rsi_mid_prev + self.rsi_all_prev

        # strategy holds by default
        decision = Decision.HOLD

        # condition for LONG
        condition = atr_all > atr_last and \
            rsi_last > 0 and \
            rsi_mid < 100 and \
            rsi_all > 0 and \
            rsi_last + rsi_mid + rsi_all > 0 and \
            rsi_last + rsi_mid + rsi_all > 0 * rsi_prev

        # perform LONG when conditions meet
        if condition:
            stoploss = candle.low
            take_profit = candle.high
            if not self.stoploss:
                self.set_stoploss(stoploss)
            if not self.take_profit:
                self.set_take_profit(take_profit)
            decision = Decision.LONG

        # update prev step
        self.rsi_last_prev = rsi_last
        self.rsi_mid_prev = rsi_mid
        self.rsi_all_prev = rsi_all

        return decision
