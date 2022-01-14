from agent import *
from gym_env import SingleAssetEnv, sample_config
from data.download import download
from callbacks import *
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback
from loguru import logger


class SingleTrainer:
    def __init__(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str,
        initial_amount: float,
        commission: float,
    ):
        self.env_type = None
        self.agent_type = None
        self.env = None
        self.agent = None
        self.symbol = symbol
        self.start_date = start
        self.end_date = end
        self.interval = interval
        self.initial_amount = initial_amount
        self.commission = commission

    @property
    @abstractmethod
    def model_path(self) -> str:
        """
        Path where to save the trained agent model
        """

    def _config(self):
        return {
            "symbol": self.symbol,
            "start": self.start_date,
            "end": self.end_date,
            "interval": self.interval,
            "initial_amount": self.initial_amount,
            "commission": self.commission,
        }

    @abstractmethod
    def _download(self):
        """
        Download data if necessary
        """

    @abstractmethod
    def _initialize_env(self):
        """
        Initialize environment
        """

    @abstractmethod
    def _initialize_agent(self):
        """
        Initialize agent
        """

    @abstractmethod
    def train(self, total_timesteps: int, **kwargs):
        """
        Train agent in the environment
        """

    @abstractmethod
    def reset(self):
        """
        Reset trainer
        """

    def load_agent(self, path: str = None):
        path = self.model_path if path is None else path
        self.agent.load(path)


class SingleDQNTrainer(SingleTrainer):
    def __init__(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str,
        initial_amount: float,
        commission: float = 0,
    ):
        super(SingleDQNTrainer, self).__init__(
            symbol, start, end, interval, initial_amount, commission
        )

        self.agent_type = SingleDQNAgent
        self.env_type = SingleAssetEnv
        self._initialize_env()
        self._initialize_agent()

    @property
    def model_path(self):
        trainer_type = "single_dqn_model"
        return f"{trainer_type}_{self.symbol}_{self.start_date}_{self.end_date}_{self.interval}"

    def _download(self):
        download([self.symbol], [self.interval], self.start_date, self.end_date)

    def _initialize_env(self):
        try:
            self.env = self.env_type(self._config())
        except AttributeError:
            self._download()
            self.env = self.env_type(self._config())

    def _initialize_agent(self):
        self.agent = self.agent_type(self.env)

    def train(self, total_timesteps: int, monitor_freq=None, **kwargs):
        # if monitor_freq:
        #     callback = kwargs.get("callback", [])
        #     eval_env = Monitor(self.env)
        #     eval_callback = EvalCallback(
        #         eval_env,
        #         best_model_save_path="./logs/",
        #         log_path="./logs/",
        #         eval_freq=monitor_freq,
        #         deterministic=True,
        #         render=False,
        #     )
        #     callback.append(eval_callback)
        #     kwargs["callback"] = callback
        logger.info("Started training...")
        self.agent.learn(total_timesteps, **kwargs)
        self.agent.save(self.model_path)
        logger.info("Finished training")
        logger.info(f"Saved model to {self.model_path}")

    def reset(self):
        self._initialize_env()
        self._initialize_agent()


# t = SingleDQNTrainer(**sample_config)
# steps = 1e4
# t.train(steps, callback=ProgressBar(steps))
# t.load_agent()
# t.env.step(1)
