import numpy as np
from gym import spaces, Env
from backtest import Ledger, Trade
from enum import Enum
from data.query import get_ohlcv
from candles import Candle


class Action(Enum):
    HOLD = 0
    BUY = 1
    SELL = 2


sample_config = {
    "symbol": "ETH",
    "start": "2018-01-01",
    "end": "2019-02-01",
    "interval": "1m",
    "initial_amount": 10000,
    "commission": 0.00075,
}


class SingleAssetEnv(Env):
    def __init__(self, config):
        super(SingleAssetEnv, self).__init__()
        self.config = config
        self.cash = config["initial_amount"]
        self.position = 0.0
        self.curr_balance = self.cash
        self.curr_trade: Trade = None
        self.ledger = Ledger(self.config["initial_amount"])
        self.commission = config.get("commission", 0)
        self.step_idx = 0
        self.df = get_ohlcv(
            asset=self.config["symbol"],
            start=self.config["start"],
            end=self.config["end"],
            interval=self.config["interval"],
        )
        n_actions = len(Action)
        self.action_space = spaces.Discrete(n_actions)
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0]),
            high=np.array([int(1e5), int(1e5), int(1e5), int(1e5), int(1e5), 1]),
        )  # OHLCV + is_trading

    def balance(self, asset_price):
        return self.cash + self.position * asset_price

    def buy(self, candle: Candle):
        if self.curr_trade:
            return
        asset_price = candle.close
        commission = self.commission * self.cash
        self.cash -= commission
        # TODO: round number of units in real trading
        num_units = self.cash / asset_price
        self.curr_trade = Trade(
            start=candle.timestamp,
            price_start=asset_price,
            num_units=num_units,
            trigger_start=Action.BUY,
            idx=self.step_idx,
            commission=commission,
        )
        self.cash = 0
        self.position += num_units

    def sell(self, candle: Candle):
        if not self.curr_trade:
            return
        # perform trade exit
        asset_price = candle.close
        gain = self.position * asset_price
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
        candle = Candle.from_df(self.df.iloc[self.step_idx])
        if action == Action.BUY:
            self.buy(candle)

        elif action == Action.SELL:
            self.sell(candle)

        self.step_idx += 1
        balance = self.balance(candle.close)
        reward = balance - self.curr_balance
        self.curr_balance = balance
        observation = (
            candle.as_array()
        )  # TODO should we take the next candle as observation? (after increasing the step idx)
        is_trading = 0 if self.curr_trade is None else 1
        observation = np.append(observation, is_trading)
        done = self.step_idx == len(self.df)
        info = {}

        return observation, reward, done, info

    def reset(self):
        self.step_idx = 0
        self.cash = self.config["initial_amount"]
        self.position = 0.0
        self.curr_balance = self.cash
        self.curr_trade = None
        self.ledger = Ledger(self.config["initial_amount"])
