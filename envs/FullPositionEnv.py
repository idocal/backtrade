import numpy as np
import pandas as pd
from loguru import logger
from gym import spaces, Env
from envs.utils import Ledger, Trade
from candles import Candle


class FullPositionEnv(Env):
    """
    Actions:
    0      : Hold
    1      : Sell
    2-(n+1): BUY (n-1)th asset
    """

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
        self.prev_vector = self.df.iloc[0]
        n_actions = len(symbols) + 2  # HOLD and SELL
        self.action_space = spaces.Discrete(n_actions)
        self.candle_low_bound = np.array([-1, -1, -1, -1, -100] * len(symbols))
        self.candle_high_bound = np.array([1, 1, 1, 1, 100] * len(symbols))
        self.observation_space = spaces.Box(
            low=np.append(self.candle_low_bound, 0),
            high=np.append(self.candle_high_bound, 1)
        )  # OHLCV + is_trading

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
            start=timestamp,
            price_start=asset_price,
            num_units=num_units,
            idx=self.step_idx,
            commission=commission,
            symbol=self.symbols[symbol_idx]
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
        self.curr_trade.end = timestamp
        self.curr_trade.price_end = asset_price
        self.curr_trade.commission += commission
        self.ledger.log_trade(self.curr_trade)

        # reset for next trade
        self.curr_trade = None

    def _observation_from_vector(self, vector):
        bounds = np.stack((self.candle_low_bound, self.candle_high_bound))
        obs = vector.relative_to(self.prev_vector, bounds=bounds).as_array()
        is_trading = 0 if self.curr_trade is None else 1
        obs = np.append(obs, is_trading)
        return obs

    def step(self, action: int):
        if self.step_idx % 100 == 0:
            logger.debug(f"Evaluating candle {self.step_idx}/{len(self.df)}")
            logger.debug(f"Taking action: {action}")
        candles = self.df.iloc[self.step_idx]
        is_legal_action = True
        reward = 0
        if action > 1:  # BUY asset
            if self.curr_trade:
                # cannot perform buy action while in position
                if self.step_idx % 100 == 0:
                    logger.warning(f"Action {action} is illegal!")
                is_legal_action = False
                reward = float('-inf')
            else:
                symbol_idx = action - 2
                candle = Candle.from_df(candles[symbol_idx:symbol_idx + 4])
                self.buy(candle, symbol_idx)

        elif action == 1:
            if self.curr_trade is None:
                # cannot perform sell action while not in position
                if self.step_idx % 100 == 0:
                    logger.warning(f"Action {action} is illegal!")
                is_legal_action = False
                reward = float('-inf')
            else:
                symbol_idx = self.symbols.index(self.curr_trade.symbol)
                candle = Candle.from_df(candles[symbol_idx:symbol_idx + 4])
                self.sell(candle)

        self.curr_balance = self.balance(candle.close)  # TODO: this does not hold for all cases
        self.ledger.log_balance(self.curr_balance, candle.timestamp)
        if is_legal_action:
            reward = self.curr_balance - self.config["initial_amount"]
        self.step_idx += 1  # start from the 2nd observation
        self.prev_vector = candle
        next_vector = self.df.iloc[self.step_idx]
        observation = self._observation_from_vector(next_vector)
        done = self.step_idx == len(self.df) - 1
        info = {}

        return observation, reward, done, info

    def reset(self):
        self.step_idx = 1
        self.cash = self.config["initial_amount"]
        self.position = 0.0
        self.prev_vector = self.df.iloc[0]
        self.curr_balance = self.cash
        self.curr_trade = None
        self.ledger = Ledger(self.config["initial_amount"])
        first_vector = self.df.iloc[1]
        return self._observation_from_candle(first_vector)
