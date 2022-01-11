from typing import Type, Union, Optional, Dict, Any
from abc import abstractmethod

from stable_baselines3 import DQN
from stable_baselines3.common.base_class import BasePolicy, BaseAlgorithm

from strategies.strategy import Strategy
from gym_env import SingleAssetEnv


class SingleAgent:
    def __init__(
        self,
        algorithm: Type[BaseAlgorithm],
        env: SingleAssetEnv,
        policy: Union[str, Type[BasePolicy]],
        algorithm_kwargs: Optional[Dict[str, Any]] = None,
        policy_kwargs: Optional[Dict[str, Any]] = None,
    ):
        self.algorithm = algorithm
        self.env = env
        self.policy = policy
        self.algorithm_kwargs = {} if algorithm_kwargs is None else algorithm_kwargs
        self.policy_kwargs = policy_kwargs
        self.model = self.algorithm(
            self.policy,
            self.env,
            policy_kwargs=self.policy_kwargs,
            **self.algorithm_kwargs
        )

    @abstractmethod
    def learn(self, total_timesteps: int, **kwargs):
        """
        Learning procedure of the agent
        """

    @abstractmethod
    def preprocess(self, observation):
        """
        Pre-process observation before input to agent
        """

    @abstractmethod
    def predict(self, observation):
        """
        The output of the agent given an observation
        """

    def step(self, action):
        """
        Taking an action inside the environment
        """
        return self.env.step(action)

    @abstractmethod
    def evaluate(self, num_episodes: int):
        """
        Evaluate the agent
        """

    def save(self, path: str):
        self.model.save(path)

    def load(self, path: str):
        self.model = self.algorithm.load(path)


class SingleDQNAgent(SingleAgent):
    def __init__(
        self,
        env: SingleAssetEnv,
        policy: Union[str, Type[BasePolicy]] = "MlpPolicy",
        strategy: Type[Strategy] = None,
        algorithm_kwargs: Optional[Dict[str, Any]] = None,
        policy_kwargs: Optional[Dict[str, Any]] = None,
    ):
        super(SingleDQNAgent, self).__init__(
            DQN, env, policy, algorithm_kwargs, policy_kwargs
        )

        self.strategy = strategy

    def predict(self, observation):
        action, _ = self.model.predict(observation)
        return action

    def learn(self, total_timesteps: int, **kwargs):
        self.model.learn(total_timesteps, **kwargs)
