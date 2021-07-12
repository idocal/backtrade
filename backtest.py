import json
from candles import Candles
from loguru import logger
from strategies.SMACrossover import SMACrossover
from strategies.strategy import Strategy, Trade, Side
from typing import Type
import plotly.graph_objects as go
from datetime import datetime
from tqdm import tqdm
from data.query import get_ohlcv
import pandas as pd


class Report:

    def __init__(self, agg: dict, trades: pd.DataFrame):
        self.agg = agg
        self.trades = trades


class Ledger:

    def __init__(self, initial_amount: float):
        self.initial_amount = initial_amount
        self.trades = []
        self.balances = []
        self.dates = []
        self.trade_points = []
        self.positions = []

    def log_trade(self, trade: Trade, idx, position: float):
        self.trade_points.append(idx)
        self.trades.append(trade)
        self.positions.append(position)

    def log_balance(self, balance: float, date: datetime):
        self.balances.append(balance)
        self.dates.append(date)

    def plot_balance(self):
        f = go.Figure()
        f.add_trace(go.Scatter(x=self.dates, y=self.balances, fill='tozeroy'))
        f.show()

    def report(self):
        # aggregated report
        bs = self.balances
        periodical_return = (self.balances[-1] - self.initial_amount) / self.initial_amount
        max_drawdown = (max(bs) - min(bs)) / max(bs)
        num_trades = len(self.trades)
        win_trades_pct = len([t for t in self.trades if t.is_profitable])
        agg = {
            'Periodical Return': periodical_return,
            'Max Drawdown': max_drawdown,
            '# Trades': num_trades,
            '% Win Trades': win_trades_pct
        }

        qtys = []
        sides = []
        exits = []
        pls = []
        dates = []
        # per trade report
        for i in range(len(self.trades)):
            trade_point = self.trade_points[i]
            trade = self.trades[i]
            position = self.positions[i]
            qty = self.balances[trade_point]
            date = trade.date
            side = 'long' if trade.side == Side.LONG else 'short'
            sell_price = trade.take_profit if trade.is_profitable \
                else trade.stoploss
            sell_price *= position
            pl = (sell_price - qty) / qty
            if trade.side == Side.SHORT:
                pl = (qty - sell_price) / qty
            qtys.append(qty)
            sides.append(side)
            exits.append(sell_price)
            pls.append(pl)
            dates.append(date)

        table = {'Date': dates, 'Qty': qtys, 'Side': sides, 'Exit': exits, 'P/L': pls}
        df = pd.DataFrame.from_dict(table)
        report = Report(agg, df)
        return report


class Backtest:

    def __init__(self, config: dict, strategy_type: Type[Strategy]):
        self.config = config
        self.strategy_type = strategy_type
        self.cash = config['initial_amount']
        self.position = 0.0
        self.curr_trade: Trade = None
        self.ledger = Ledger(self.config['initial_amount'])
        self.commission = config.get('commission', 0)

    def balance(self, asset_price):
        return self.cash + self.position * asset_price

    def start_trade(self, trade, candles, idx):
        assert not self.curr_trade
        self.curr_trade = trade
        asset_price = candles.close[idx]
        # TODO: round number of units in real trading
        num_units = self.cash / asset_price
        commission = self.comission * self.cash

        if trade.side == Side.LONG:
            self.position += num_units
            self.cash = 0.0
        elif trade.side == Side.SHORT:
            self.position -= num_units
            self.cash += self.cash
        self.cash -= commission

        self.ledger.log_trade(trade, idx, num_units)

    def end_trade(self, candles, idx):
        stoploss = self.curr_trade.stoploss
        take_profit = self.curr_trade.take_profit

        # short and long conditions for execution
        long_stoploss_cond = candles.low[idx] <= stoploss
        long_take_profit_cond = candles.high[idx] >= take_profit
        short_stoploss_cond = candles.high[idx] >= stoploss
        short_take_profit_cond = candles.low[idx] <= take_profit

        def _end(price, is_profitable=True):
            gain = self.position * price
            self.cash += gain
            self.cash -= self.commission * gain
            self.position = 0.0
            self.curr_trade.is_profitable = is_profitable
            # logger.info(f"Selling asset at price {price}")
            self.curr_trade = None

        # end long trades
        if self.curr_trade.side == Side.LONG:
            if long_stoploss_cond:
                _end(stoploss, False)
            elif long_take_profit_cond:
                _end(take_profit)

        # end short trades
        elif self.curr_trade.side == Side.SHORT:
            if short_stoploss_cond:
                _end(stoploss, False)
            elif short_take_profit_cond:
                _end(take_profit)

    def run(self):
        logger.info("Beginning backtest...")
        logger.info(f"Initial amount: {self.cash}...")

        symbol = self.config['symbol']
        start = self.config['start']
        end = self.config['end']
        interval = self.config['interval']

        # download data
        data = get_ohlcv(symbol, start=start, end=end, interval=interval)
        candles = Candles(data)
        logger.info(f"Detected {len(candles)} ticks")

        # run strategy
        strategy = self.strategy_type(candles=candles)
        trades = strategy.backtest()
        non_hold = [t for t in trades if t]
        logger.info(f"Decided on {len(non_hold)} trades")

        # end trades
        for i, candle in enumerate(tqdm(candles.data.iterrows())):
            balance = self.balance(candles.close[i])
            date = candle[0]
            self.ledger.log_balance(balance, date)
            # first check for current trade termination
            if self.curr_trade:
                self.end_trade(candles, i)
            # if no active trade, register one
            elif trades[i]:
                # logger.info("New trade registered")
                # logger.info(f"{trades[i]}")
                self.start_trade(trades[i], candles, i)

        self.ledger.plot_balance()
        return self.ledger.report()


if __name__ == '__main__':
    config = json.load(open('./config.json'))
    strategy_type = SMACrossover
    backtest = Backtest(config, strategy_type)
    report = backtest.run()
