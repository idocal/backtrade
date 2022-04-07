import numpy as np
import pandas as pd
from loguru import logger
from gym import spaces, Env

from api.db import crud
from envs.utils import Ledger, Trade, Observation
from candles import Candle


class FullPositionEnv(Env):
    """
    Actions:
    0      : Hold
    1      : Sell
    2-(n+1): BUY (n-1)th asset
    """

    def __init__(self, config, symbols, data: pd.DataFrame, db=None):
        super(FullPositionEnv, self).__init__()
        self.config = config
        self.agent_id = config["agent_id"]
        self.db = db
        self.cash = config["initial_amount"]
        self.symbols = symbols
        self.position = 0.0
        self.curr_balance = self.cash
        self.curr_trade: Trade = None
        self.ledger = Ledger(self.config["initial_amount"])
        self.commission = config.get("commission", 0)
        self.step_idx = 1
        self.episode = 1
        self.df = data.drop_duplicates()
        self.prev_obs = Observation.from_df(self.df.iloc[0])
        n_actions = len(symbols) + 2  # HOLD and SELL
        self.action_space = spaces.Discrete(n_actions)
        self.candle_low_bound = np.array([-1, -1, -1, -1, -100] * len(symbols))
        self.candle_high_bound = np.array([1, 1, 1, 1, 100] * len(symbols))
        self.observation_space = spaces.Box(
            low=np.append(self.candle_low_bound, 0),
            high=np.append(self.candle_high_bound, 1),
        )  # OHLCV + is_trading
        self.actions = {
            **{0: "HOLD", 1: "SELL"},
            **{n: self.symbols[n - 2] for n in range(2, len(self.symbols) + 2)},
        }

    def balance(self, asset_price):
        return self.cash + self.position * asset_price

    def buy(self, asset_price, timestamp, symbol_idx):
        if self.curr_trade:
            return
        commission = self.commission * self.cash
        self.cash -= commission
        # TODO: round number of units in real trading
        num_units = self.cash / asset_price
        self.curr_trade = Trade(
            start_time=timestamp,
            price_start=asset_price,
            num_units=num_units,
            idx=self.step_idx,
            commission=commission,
            symbol=self.symbols[symbol_idx],
        )
        self.cash = 0
        self.position += num_units

    def sell(self, asset_price, timestamp):
        if not self.curr_trade:
            return
        # perform trade exit
        gain = self.position * asset_price
        commission = self.commission * gain
        self.cash += gain
        self.cash -= commission
        self.position = 0.0

        # log trade
        self.curr_trade.end_time = timestamp
        self.curr_trade.price_end = asset_price
        self.curr_trade.commission += commission
        self.ledger.log_trade(self.curr_trade)

        # reset for next trade
        self.curr_trade = None

    def _next_from_obs(self, obs) -> np.ndarray:
        bounds = np.stack((self.candle_low_bound, self.candle_high_bound))
        next_obs = obs.relative_to(self.prev_obs, bounds=bounds).data
        is_trading = 0 if self.curr_trade is None else 1
        next_obs = np.append(next_obs, is_trading)
        return next_obs

    def step(self, action: int):
        if self.step_idx % 100 == 0:
            logger.debug(f"Evaluating candle {self.step_idx}/{len(self.df)} | episode:{self.episode}")
            logger.debug(f"Taking action: {action}")
        candles = self.df.iloc[self.step_idx]
        obs = Observation.from_df(candles)
        is_legal_action = True
        reward = 0
        asset_price = 0

        # perform actions
        if action > 1:  # BUY asset
            if self.curr_trade:
                # cannot perform buy action while in position
                if self.step_idx % 100 == 0:
                    logger.warning(f"Action {action} is illegal!")
                is_legal_action = False
                reward = float("-inf")
            else:
                symbol_idx = action - 2
                asset_price = obs.data[symbol_idx + 4]  # close price
                self.buy(asset_price, obs.timestamp, symbol_idx)

        elif action == 1:  # SELL
            if self.curr_trade is None:
                # cannot perform sell action while not in position
                if self.step_idx % 100 == 0:
                    logger.warning(f"Action {action} is illegal!")
                is_legal_action = False
                reward = float("-inf")
            else:
                symbol_idx = self.symbols.index(self.curr_trade.symbol)
                asset_price = obs.data[symbol_idx + 4]  # close price
                self.sell(asset_price, obs.timestamp)
        else:  # HOLD
            if self.curr_trade is not None:
                symbol_idx = self.symbols.index(self.curr_trade.symbol)
                asset_price = obs.data[symbol_idx + 4]  # close price
        # update env with action
        next_balance = self.balance(
            asset_price
        )  # TODO: this does not hold for all cases

        if self.db:
            crud.update_agent(
                self.db,
                self.agent_id,
                ["action", "obs", "balance"],
                [self.actions[action], obs.data.tolist(), float(next_balance)],
            )

        self.ledger.log_balance(self.curr_balance, obs.timestamp)
        if is_legal_action:
            reward = next_balance - self.curr_balance
        self.curr_balance = next_balance

        # proceed to next step
        self.step_idx += 1  # start from the 2nd observation
        self.prev_obs = obs
        next_obs = Observation.from_df(self.df.iloc[self.step_idx])
        observation = self._next_from_obs(next_obs)
        done = self.step_idx == len(self.df) - 1
        if done:
            self.episode += 1
        info = {}

        return observation, reward, done, info

    def reset(self):
        self.step_idx = 1
        self.cash = self.config["initial_amount"]
        self.position = 0.0
        self.prev_obs = Observation.from_df(self.df.iloc[0])
        self.curr_balance = self.cash
        self.curr_trade = None
        self.ledger = Ledger(self.config["initial_amount"])
        first_obs = Observation.from_df(self.df.iloc[1])
        return self._next_from_obs(first_obs)
