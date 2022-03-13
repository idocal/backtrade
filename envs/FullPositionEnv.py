import numpy as np
import pandas as pd
from loguru import logger
from gym import spaces, Env
from backtest import Ledger, Trade
from enum import Enum
from candles import Candle, Candles


class Action(Enum):
    HOLD = 0
    BUY = 1
    SELL = 2

    def __eq__(self, o):
        if isinstance(o, Action):
            return self.value == o.value
        elif isinstance(o, int):
            return self.value == o
        else:
            raise AttributeError(f"Cannot compare Action with {type(o)}")


class FullPositionEnv(Env):
    def __init__(self, config, symbols, data: pd.DataFrame):
        super(FullPositionEnv, self).__init__()
        self.config = config
        self.cash = config["initial_amount"]
        self.symbols = symbols
        self.position = 0.0
        self.curr_balance = self.cash
        self.curr_trade: Trade = None
        self.ledger = Ledger(self.config["initial_amount"])
        self.commission = config.get("commission", 0)
        self.step_idx = 1
        self.df = data
        self.prev_candle = Candle.from_df(self.df.iloc[0])
        n_actions = len(symbols) + 2  # HOLD and SELL
        self.action_space = spaces.Discrete(n_actions)
        self.candle_low_bound = np.array([-1, -1, -1, -1, -100] * len(symbols))
        self.candle_high_bound = np.array([1, 1, 1, 1, 100] * len(symbols))
        self.observation_space = spaces.Box(
            low=np.append(self.candle_low_bound, 0),
            high=np.append(self.candle_high_bound, 1)
        )  # OHLCV + is_trading

    def plot_candles(self, num: int = np.inf):
        candles = Candles(self.df[:num])
        candles.plot()

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

    def _observation_from_candle(self, candle: Candle):
        bounds = np.stack((self.candle_low_bound, self.candle_high_bound))
        obs = candle.relative_to(self.prev_candle, bounds=bounds).as_array()
        is_trading = 0 if self.curr_trade is None else 1
        obs = np.append(obs, is_trading)
        return obs

    def step(self, action: Action):
        if self.step_idx % 100 == 0:
            logger.debug(f"Evaluating candle {self.step_idx}/{len(self.df)}")
            logger.debug(f"Taking action: {action}")
        candle = Candle.from_df(self.df.iloc[self.step_idx])
        is_legal_action = True
        reward = 0
        if action == Action.BUY:
            if self.curr_trade:
                # cannot perform buy action while in position
                if self.step_idx % 100 == 0:
                    logger.warning(f"Action {action} is illegal!")
                is_legal_action = False
                reward = float('-inf')
            else:
                self.buy(candle)

        elif action == Action.SELL:
            if self.curr_trade is None:
                # cannot perform sell action while not in position
                if self.step_idx % 100 == 0:
                    logger.warning(f"Action {action} is illegal!")
                is_legal_action = False
                reward = float('-inf')
            else:
                self.sell(candle)

        self.curr_balance = self.balance(candle.close)
        self.ledger.log_balance(self.curr_balance, candle.timestamp)
        if is_legal_action:
            reward = self.curr_balance - self.config["initial_amount"]
        self.step_idx += 1  # start from the 2nd observation
        self.prev_candle = candle
        next_candle = Candle.from_df(self.df.iloc[self.step_idx])
        observation = self._observation_from_candle(next_candle)
        done = self.step_idx == len(self.df) - 1
        info = {}

        return observation, reward, done, info

    def reset(self):
        self.step_idx = 1
        self.cash = self.config["initial_amount"]
        self.position = 0.0
        self.prev_candle = Candle.from_df(self.df.iloc[0])
        self.curr_balance = self.cash
        self.curr_trade = None
        self.ledger = Ledger(self.config["initial_amount"])
        first_candle = Candle.from_df(self.df.iloc[1])
        return self._observation_from_candle(first_candle)
