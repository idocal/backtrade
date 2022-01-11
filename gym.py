import gym
import numpy as np
from gym import spaces
from backtest import Ledger, Trade
from enum import Enum
from data.query import get_ohlcv
from candles import Candle


class Action(Enum):
    HOLD = 0
    BUY = 1
    SELL = 2


sample_config = {
    "symbol": "BTC",
    "start": "2021-01-01",
    "end": "2021-02-01",
    "interval": "1m",
    "initial_amount": 10000,
    "commission": 0.00075
}


class SingleAssetEnv(gym.Env):

    def __init__(self, config):
        super(SingleAssetEnv, self).__init__()
        self.config = config
        self.cash = config['initial_amount']
        self.position = 0.0
        self.balance = self.cash
        self.curr_trade: Trade = None
        self.ledger = Ledger(self.config['initial_amount'])
        self.commission = config.get('commission', 0)
        self.step_idx = 0
        self.df = get_ohlcv(symbol=self.config['symbol'],
                            start=self.config['start'],
                            end=self.config['end'],
                            interval=self.config['interval'])
        n_actions = len(Action)
        self.action_space = spaces.Discrete(n_actions)
        self.observation_space = spaces.Box(shape=(6,))  # OHLCV + is_trading

    def balance(self, asset_price):
        return self.cash + self.position * asset_price

    def buy(self, candle):
        if self.curr_trade:
            return
        asset_price = candle.close
        # TODO: round number of units in real trading
        num_units = self.cash / asset_price
        commission = self.commission * self.cash
        self.cash -= commission
        self.curr_trade = Trade(
            start=candle.timestamp,
            price_start=asset_price,
            num_units=num_units,
            trigger_start=Action.BUY,
            idx=self.step_idx,
            commission=commission
        )

    def sell(self, candle: Candle):
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
        self.curr_trade.trigger_end = Action.SELL
        self.curr_trade.commission += commission
        self.ledger.log_trade(self.curr_trade)

        # reset for next trade
        self.curr_trade = None

    def step(self, action: Action):
        candle = self.df.iloc[self.step_idx]
        if action == Action.BUY:
            self.buy(candle)

        elif action == Action.SELL:
            self.sell(candle)

        self.step_idx += 1
        balance = self.balance()
        reward = self.balance() - self.curr_balance
        self.curr_balance = balance
        observation = candle.as_array()
        is_trading = 0 if self.curr_trade is None else 1
        observation = np.append(observation, is_trading)
        done = self.step_idx == len(self.df)
        info = {}

        return observation, reward, done, info
