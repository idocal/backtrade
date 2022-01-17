import json
from agents.agent import SingleAgent
from envs.SingleAssetEnv import SingleAssetEnv
from stable_baselines3 import DQN
from envs.SingleAssetEnv import Action


class NaiveAgent(SingleAgent):

    def __init__(self):
        config = json.load(open("config.json"))
        env = SingleAssetEnv(config)
        super(NaiveAgent, self).__init__(DQN, env, "MlpPolicy")
        self.predicted = False

    def predict(self, observation):
        if self.predicted:
            return Action.HOLD
        else:
            self.predicted = True
            return Action.BUY
