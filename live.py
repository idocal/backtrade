import json
from strategies.strategy import Trade, Strategy
from strategies.SMACrossover import SMACrossover
from utils import env_vars
from binance.websocket.spot.websocket_client import SpotWebsocketClient as Client

STREAM_URI = 'wss://stream.binance.com:9443/ws'


class Live:

    def __init__(self, config: dict, strategy: Strategy):
        self.strategy = strategy
        self.client = Client()
        self.client.start()
        self.config = config
        self.symbol = config['symbol'] + 'usdt'

    def message_handler(self, message):
        print(message)

    def get_candles(self):
        interval = self.config['interval']
        self.client.kline(symbol=self.symbol,
                          id=1,
                          interval=interval,
                          callback=self.message_handler)

    def order(self, key, trade: Trade):
        request = {
            "symbol": self.symbol,
            "side": "BUY"
        }


if __name__ == '__main__':
    config = json.load(open('./config.json'))
    env = env_vars()
    api_key = env['API_KEY']
    api_secret = env['API_SECRET']
    strategy = SMACrossover()
    live = Live(config, strategy)
    live.get_candles()
