import json
import yfinance as yf
from candles import Candles
from indicator import SMA

if __name__ == '__main__':
    # configuration
    config = json.load(open('./config.json'))
    symbol = config['symbol']
    start = config['start']
    end = config['end']
    interval = config['interval']

    # download data
    data = yf.download(symbol, start=start, end=end, interval=interval)

    # candle
    candles = Candles(data)

    # indicator
    sma100 = SMA(data=candles, window=100)
    sma200 = SMA(data=candles, window=200)
    candles.plot(indicators=[sma100, sma200])
