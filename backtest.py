import json
import yfinance as yf
from candles import Candles
from strategy import SMACrossover
from loguru import logger
from strategy import Decision


class Backtest:

    def __init__(self, config: dict):
        self.config = config
        self.cash = config['initial_amount']
        self.holdings = 0

    def balance(self, asset_price):
        return self.cash + self.holdings * asset_price

    def run(self):
        logger.info("Beginning backtest...")

        symbol = self.config['symbol']
        start = self.config['start']
        end = self.config['end']
        interval = self.config['interval']

        # download data
        data = yf.download(symbol, start=start, end=end, interval=interval)
        candles = Candles(data)
        logger.debug(f"Detected {len(candles)} ticks")

        # strategy
        strategy = SMACrossover(data=candles)
        positions = strategy.backtest()
        non_hold = [p for p in positions if p.decision != Decision.HOLD]
        logger.debug(f"Decided on {len(non_hold)} positions")

        # execute positions
        for i, position in enumerate(positions):
            asset_price = candles.close[i]
            if position.decision == Decision.HOLD:
                continue
            if position.decision == Decision.BUY:
                investment = position.amount * self.cash
                self.cash -= investment
                self.holdings += investment / asset_price
                logger.info(f"Buying ${investment} of {symbol}")
            elif position.decision == Decision.SELL:
                sell_holdings = position.amount * self.holdings
                self.cash += asset_price * sell_holdings
                self.holdings -= sell_holdings
                logger.info(f"Selling {sell_holdings:.4f} of {symbol}")
            current_balance = self.balance(asset_price)
            logger.info(f"Current balance: {current_balance}")


if __name__ == '__main__':
    config = json.load(open('./config.json'))
    backtest = Backtest(config)
    backtest.run()
