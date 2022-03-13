import datetime

from data.query import get_ohlcv
from data.query import MissingDataError
from data.download import download
from envs.SingleAssetEnv import SingleAssetEnv
from agents.SingleDQNAgent import SingleDQNAgent

from stable_baselines3.common.env_checker import check_env


def initialize_agent_env(request: dict):
    start = datetime.datetime.strptime(request["start"].split("T")[0], "%Y-%m-%d")
    end = datetime.datetime.strptime(request["end"].split("T")[0], "%Y-%m-%d")
    try:
        df = get_ohlcv(request["symbol"], start, end, request["interval"])
    except MissingDataError:
        download(
            request["provider"], request["symbol"], request["interval"], start, end
        )
        df = get_ohlcv(request["symbol"], start, end, request["interval"])
    env = SingleAssetEnv(request, df)
    check_env(env)
    agent = SingleDQNAgent(env)

    return agent, env
