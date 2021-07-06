import json
import yfinance as yf
from candles import Candles
from loguru import logger
from strategies.SMACrossover import SMACrossover
from strategies.strategy import Strategy, Trade, Side
from typing import Type
import plotly.graph_objects as go


class Ledger:

    def __init__(self):
        self.trades = []
        self.balances = []

    def log_trade(self, trade: Trade):
        self.trades.append(trade)

    def log_balance(self, balance: float):
        self.balances.append(balance)

    def plot_balance(self):
        fig = go.Figure()
        x = [i for i in range(len(self.balances))]
        fig.add_trace(go.Scatter(x=x, y=self.balances, fill='tozeroy'))
        fig.show()


class Backtest:

    def __init__(self, config: dict, strategy_type: Type[Strategy]):
        self.config = config
        self.strategy_type = strategy_type
        self.cash = config['initial_amount']
        self.position = 0.0
        self.curr_trade: Trade = None
        self.ledger = Ledger()

    def balance(self, asset_price):
        return self.cash + self.position * asset_price

    def start_trade(self, trade, candles, idx):
        assert not self.curr_trade
        self.curr_trade = trade
        asset_price = candles.close[idx]
        # TODO: round number of units in real trading
        num_units = self.cash / asset_price

        if trade.side == Side.LONG:
            self.position += num_units
            self.cash = 0.0
        elif trade.side == Side.SHORT:
            self.position -= num_units
            self.cash += self.cash

    def end_trade(self, candles, idx):
        stoploss = self.curr_trade.stoploss
        take_profit = self.curr_trade.take_profit

        # short and long conditions for execution
        long_stoploss_cond = candles.low[idx] <= stoploss
        long_take_profit_cond = candles.high[idx] >= take_profit
        short_stoploss_cond = candles.high[idx] >= stoploss
        short_take_profit_cond = candles.low[idx] <= take_profit

        def _end_long(price):
            self.cash += self.position * price
            self.position = 0.0
            logger.info(f"Selling asset at price {price}")
            self.curr_trade = None

        def _end_short(price):
            self.cash += self.position * price
            self.position = 0.0
            logger.info(f"Buying asset at price {price}")
            self.curr_trade = None

        # end long trades
        if self.curr_trade.side == Side.LONG:
            if long_stoploss_cond:
                _end_long(stoploss)
            elif long_take_profit_cond:
                _end_long(take_profit)

        # end short trades
        elif self.curr_trade.side == Side.SHORT:
            if short_stoploss_cond:
                _end_short(stoploss)
            elif short_take_profit_cond:
                _end_short(take_profit)

    def run(self):
        logger.info("Beginning backtest...")
        logger.info(f"Initial amount: {self.cash}...")

        symbol = self.config['symbol']
        start = self.config['start']
        end = self.config['end']
        interval = self.config['interval']

        # download data
        data = yf.download(symbol, start=start, end=end, interval=interval)
        candles = Candles(data)
        logger.info(f"Detected {len(candles)} ticks")

        # run strategy
        strategy = self.strategy_type(candles=candles)
        trades = strategy.backtest()
        non_hold = [t for t in trades if t]
        logger.info(f"Decided on {len(non_hold)} trades")

        # end trades
        for i, candle in enumerate(candles.data.iterrows()):
            asset_price = candles.close[i]
            balance = self.balance(candles.close[i])
            logger.debug(f"Current balance: {balance}\tasset price: {asset_price}")
            self.ledger.log_balance(balance)
            # first check for current trade termination
            if self.curr_trade:
                self.end_trade(candles, i)
            # if no active trade, register one
            elif trades[i]:
                logger.info("New trade registered")
                logger.info(f"{trades[i]}")
                self.start_trade(trades[i], candles, i)

        self.ledger.plot_balance()


if __name__ == '__main__':
    config = json.load(open('./config.json'))
    strategy_type = SMACrossover
    backtest = Backtest(config, strategy_type)
    backtest.run()
