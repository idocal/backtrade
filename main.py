import json
from candles import Candles
from indicators.SMA import SMA
from indicators.RSI import RSI
from query import get_ohlcv

if __name__ == '__main__':
    # configuration
    config = json.load(open('./config.json'))
    symbol = config['symbol']
    start = config['start']
    end = config['end']
    interval = config['interval']

    # download data
    # data = yf.download(symbol, start=start, end=end, interval=interval)
    data = get_ohlcv(symbol, start, end, interval)

    # candle
    candles = Candles(data)

    # indicator
    sma100 = SMA(period=100)
    sma200 = SMA(period=200)
    rsi100 = RSI(period=100)
    candles.plot(indicators=[sma100, sma200, rsi100])
