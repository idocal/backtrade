from typing import Type, Union, Optional, Dict, Any
from agents.agent import SingleAgent
from strategies.strategy import Strategy
from envs.SingleAssetEnv import SingleAssetEnv
from stable_baselines3 import DQN
from stable_baselines3.common.base_class import BasePolicy


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


if __name__ == "__main__":
    import json
    c = json.load(open("config.json"))
    env = SingleAssetEnv(c)
    agent = SingleDQNAgent(env)
