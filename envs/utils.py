from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import plotly.graph_objects as go
import pandas as pd


class Decision(Enum):
    HOLD = 0
    LONG = 1
    SHORT = 2
    PULL = 3
    STOPLOSS = 4
    TAKE_PROFIT = 5

    def __str__(self):
        d = {
            0: "hold",
            1: "long",
            2: "short",
            3: "pull",
            4: "stoploss",
            5: "take profit",
        }
        return d[self.value]


@dataclass
class Trade:
    start_time: datetime
    price_start: float
    num_units: float
    trigger_start: Decision
    idx: int
    commission: float
    end_time: datetime = None
    price_end: float = None
    trigger_end: Decision = None

    def as_dict(self):
        return {"start_time": self.start_time,
                "price_start": self.price_start,
                "num_units": self.num_units,
                "trigger_start": self.trigger_start.value,
                "idx": self.idx,
                "commission": self.commission,
                "end_time": self.end_time,
                "price_end": self.price_end,
                "trigger_end": self.trigger_end.value,
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
        num_stoploss = len(
            [t for t in self.trades if t.trigger_end == Decision.STOPLOSS]
        )
        num_take_profit = len(
            [t for t in self.trades if t.trigger_end == Decision.TAKE_PROFIT]
        )
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
            "Stoploss": num_stoploss,
            "Take Profit": num_take_profit,
            "Profitable Trades": profitable,
            "Commission": sum(commissions),
        }
        df = pd.DataFrame.from_dict(table)
        report = Report(agg, df)
        return report
