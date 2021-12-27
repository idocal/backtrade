import pandas as pd
import matplotlib as plt
import random
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Candle:

    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime

    def from_df(df_row: pd.Series):
        timestamp = datetime.fromisoformat(df_row.name)
        return Candle(
            open=df_row['Open'],
            high=df_row['High'],
            low=df_row['Low'],
            close=df_row['Close'],
            volume=df_row['Volume'],
            timestamp=timestamp
        )


class Candles:

    def __init__(self, data: pd.DataFrame = None):
        self.cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        self.index = 'Date'

        if data is None:
            data = pd.DataFrame(columns=self.cols)

        assert all([col in data.columns for col in self.cols])
        self._data = data
        self.colors = [h for name, h in plt.colors.cnames.items()]

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return self.data.__repr__

    def __iter__(self):
        for i in range(len(self.data)):
            yield Candle.from_df(self.data.iloc[i])

    @property
    def open(self) -> pd.Series:
        return self.data['Open']

    @property
    def high(self) -> pd.Series:
        return self.data['High']

    @property
    def low(self) -> pd.Series:
        return self.data['Low']

    @property
    def close(self) -> pd.Series:
        return self.data['Close']

    @property
    def volume(self) -> pd.Series:
        return self.data['Volume']

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    def add(self, _date: datetime, _open, _high, _low, _close, _volume):
        data = [[_date, _open, _high, _low, _close, _volume]]
        row = pd.DataFrame(data, columns=self.cols, index=[_date])
        self._data = self._data.append(row)

    def random_color(self):
        return self.colors.pop(random.randrange(len(self.colors)))

    def accumulate(self, k):
        group = self.data.groupby(np.arange(len(self)) // k)
        agg = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }
        data = group.agg(agg)
        return Candles(data=data)

    def plot(self, indicators=[]):
        # plot candlesticks
        candlesticks_data = go.Candlestick(x=self.data.index,
                                           open=self.open,
                                           high=self.high,
                                           low=self.low,
                                           close=self.close)
        fig = go.Figure(data=[candlesticks_data])

        # add indicators on top
        for indicator in indicators:
            values = [indicator.next(c) for c in self]
            color = self.random_color()
            line = go.Scatter(x=self.data.index,
                              y=values,
                              mode="lines",
                              name=indicator.name,
                              line=go.scatter.Line(color=color))
            fig.add_trace(line)

        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()
