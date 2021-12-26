import json
from candles import Candles, Candle
from loguru import logger
from strategies.ATRStrategy import ATRStrategy
# from strategies.SMACrossover import SMACrossover
from strategies.strategy import Strategy, Decision
from typing import Type
import plotly.graph_objects as go
from datetime import datetime
from tqdm import tqdm
from query import get_ohlcv
import pandas as pd
from dataclasses import dataclass


@dataclass
class Trade:
    start: datetime
    price_start: float
    num_units: float
    trigger_start: Decision
    idx: int
    commission: float
    end: datetime = None
    price_end: float = None
    trigger_end: Decision = None


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

    def log_trade(self, trade: Trade):
        self.trade_points.append(trade.idx)
        self.trades.append(trade)

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
        num_stoploss = len([t for t in self.trades if t.trigger_end ==
                            Decision.STOPLOSS])
        num_take_profit = len([t for t in self.trades if t.trigger_end ==
                               Decision.TAKE_PROFIT])
        profitable = len([t for t in self.trades if t.price_end - t.price_start
                          > 0])

        start_dates = [t.start for t in self.trades]
        price_starts = [t.price_start for t in self.trades]
        trigger_starts = [str(t.trigger_start) for t in self.trades]
        positions = [t.num_units for t in self.trades]
        end_dates = [t.end for t in self.trades]
        price_ends = [t.price_end for t in self.trades]
        trigger_ends = [str(t.trigger_end) for t in self.trades]
        trade_balances = [self.balances[t.idx] for t in self.trades]
        commissions = [t.commission for t in self.trades]

        table = {'Start Date': start_dates, 'Price Start': price_starts,
                 'Price End': price_ends, 'Trigger Start': trigger_starts,
                 'Trigger End': trigger_ends, 'Position': positions,
                 'End Date': end_dates, 'Balance': trade_balances,
                 'Commission': commissions}

        agg = {
            'Periodical Return': periodical_return,
            'Max Drawdown': max_drawdown,
            '# Trades': num_trades,
            'Stoploss': num_stoploss,
            'Take Profit': num_take_profit,
            'Profitable Trades': profitable,
            'Commission': sum(commissions)
        }
        df = pd.DataFrame.from_dict(table)
        report = Report(agg, df)
        return report


class Backtest:

    def __init__(self, config: dict, strategy_type: Type[Strategy]):
        self.config = config
        self.strategy_type = strategy_type
        self.strategy = strategy_type()
        self.cash = config['initial_amount']
        self.position = 0.0
        self.curr_trade: Decision = None
        self.ledger = Ledger(self.config['initial_amount'])
        self.commission = config.get('commission', 0)

    def balance(self, asset_price):
        return self.cash + self.position * asset_price

    def start_trade(self, decision, candle, idx):
        if self.curr_trade:
            return
        asset_price = candle.close
        # TODO: round number of units in real trading
        num_units = self.cash / asset_price
        commission = self.commission * self.cash
        self.curr_trade = Trade(
            start=candle.timestamp,
            price_start=asset_price,
            num_units=num_units,
            trigger_start=decision,
            idx=idx,
            commission=commission
        )

        if decision == Decision.LONG:
            self.position += num_units
            self.cash = 0.0
        elif decision == Decision.SHORT:
            self.position -= num_units
            self.cash += self.cash
        self.cash -= commission
        # self.ledger.log_trade(decision, idx, num_units)

    def end_trade(self, decision, candle):
        if not self.curr_trade:
            return
        # perform trade exit
        price = candle.close
        gain = self.position * price
        commission = self.commission * gain
        self.cash += gain
        self.cash -= commission
        self.position = 0.0

        # log trade
        self.curr_trade.end = candle.timestamp
        self.curr_trade.price_end = candle.close
        self.curr_trade.trigger_end = decision
        self.curr_trade.commission += commission
        self.ledger.log_trade(self.curr_trade)

        # reset for next trade
        self.strategy.set_stoploss(None)
        self.strategy.set_take_profit(None)
        self.curr_trade = None

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
        for i in tqdm(range(len(candles))):
            candle = Candle.from_df(candles.data.iloc[i])
            starts = [Decision.SHORT, Decision.LONG]
            ends = [Decision.PULL, Decision.STOPLOSS, Decision.TAKE_PROFIT]
            decision = self.strategy.process(candle)

            if decision in starts:
                self.start_trade(decision, candle, i)
            elif decision in ends:
                self.end_trade(decision, candle)

            balance = self.balance(candle.close)
            date = candle.timestamp
            self.ledger.log_balance(balance, date)

        self.ledger.plot_balance()
        return self.ledger.report()


if __name__ == '__main__':
    config = json.load(open('./config.json'))
    strategy_type = ATRStrategy
    backtest = Backtest(config, strategy_type)
    report = backtest.run()
