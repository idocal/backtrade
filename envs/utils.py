from dataclasses import dataclass
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
import numpy as np


@dataclass
class Observation:
    timestamp: datetime
    data: np.ndarray

    @staticmethod
    def from_df(df: pd.Series):
        data = df.to_numpy()
        timestamp = pd.to_datetime(df.name)
        return Observation(timestamp=timestamp, data=data)

    def relative_to(self, obs, bounds=None):
        assert self.data.shape == obs.data.shape
        rel_obs = (self.data - obs.data) / obs.data
        if bounds is not None:
            np.clip(rel_obs, bounds[0], bounds[1], out=rel_obs)
        return Observation(timestamp=self.timestamp, data=rel_obs)


@dataclass
class Trade:
    start_time: datetime
    price_start: float
    num_units: float
    idx: int
    commission: float
    end_time: datetime = None
    price_end: float = None
    symbol: str = ""

    def as_dict(self):
        return {
            "start_time": self.start_time,
            "price_start": self.price_start,
            "num_units": self.num_units,
            "idx": self.idx,
            "commission": self.commission,
            "end_time": self.end_time,
            "price_end": self.price_end,
        }


class Report:
    def __init__(self, agg: dict, trades: pd.DataFrame):
        self.agg = agg
        self.trades = trades


class Ledger:
    def __init__(self, initial_amount: float):
        self.initial_amount = initial_amount
        self.trades = []
        self.balances = []
        self.timestamps = []
        self.trade_points = []

    def get_data(self):
        return {
            "initial_amounts": self.initial_amount,
            "trades": self.trades,
            "balances": self.balances,
            "timestamps": self.timestamps,
            "trade_points": self.trade_points,
        }

    def log_trade(self, trade: Trade):
        self.trade_points.append(trade.idx)
        self.trades.append(trade)

    def log_balance(self, balance: float, date: datetime):
        self.balances.append(balance)
        self.timestamps.append(date)

    def plot_balance(self):
        f = go.Figure()
        f.add_trace(go.Scatter(x=self.timestamps, y=self.balances, fill="tozeroy"))
        f.show()

    def report(self):
        # aggregated report
        bs = self.balances
        periodical_return = (
            self.balances[-1] - self.initial_amount
        ) / self.initial_amount
        max_drawdown = (max(bs) - min(bs)) / max(bs)
        num_trades = len(self.trades)
        profitable = len([t for t in self.trades if t.price_end - t.price_start > 0])

        start_dates = [t.start_time for t in self.trades]
        price_starts = [t.price_start for t in self.trades]
        trigger_starts = [str(t.trigger_start) for t in self.trades]
        positions = [t.num_units for t in self.trades]
        end_dates = [t.end_time for t in self.trades]
        price_ends = [t.price_end for t in self.trades]
        trigger_ends = [str(t.trigger_end) for t in self.trades]
        trade_balances = [self.balances[t.idx] for t in self.trades]
        commissions = [t.commission for t in self.trades]

        table = {
            "Start Date": start_dates,
            "Price Start": price_starts,
            "Price End": price_ends,
            "Trigger Start": trigger_starts,
            "Trigger End": trigger_ends,
            "Position": positions,
            "End Date": end_dates,
            "Balance": trade_balances,
            "Commission": commissions,
        }

        agg = {
            "Periodical Return": periodical_return,
            "Max Drawdown": max_drawdown,
            "# Trades": num_trades,
            "Profitable Trades": profitable,
            "Commission": sum(commissions),
        }
        df = pd.DataFrame.from_dict(table)
        report = Report(agg, df)
        return report
