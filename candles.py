import pandas as pd
import matplotlib as plt
import random
import plotly.graph_objects as go


class Candles:

    def __init__(self, data: pd.DataFrame):
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        assert all([col in data.columns for col in required_columns])
        self._data = data
        self.colors = [h for name, h in plt.colors.cnames.items()]

    def __len__(self):
        return len(self.data)

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

    def random_color(self):
        return self.colors.pop(random.randrange(len(self.colors)))

    def plot(self, indicators=[]):
        candlesticks_data = go.Candlestick(x=self.data.index,
                                           open=self.open,
                                           high=self.high,
                                           low=self.low,
                                           close=self.close)
        fig = go.Figure(data=[candlesticks_data])
        if len(indicators):
            for indicator in indicators:
                color = self.random_color()
                line = go.Scatter(x=self.data.index,
                                  y=indicator,
                                  mode="lines",
                                  line=go.scatter.Line(color=color))
                fig.add_trace(line)
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()
