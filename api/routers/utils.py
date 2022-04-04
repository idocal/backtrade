import datetime

from data.query import get_ohlcv
from data.query import MissingDataError
from data.download import download
from envs.FullPositionEnv import FullPositionEnv
from agents.DQNAgent import DQNAgent

from stable_baselines3.common.env_checker import check_env


def initialize_agent_env(request: dict, db=None):
    start = datetime.datetime.strptime(request["start_date"].split("T")[0], "%Y-%m-%d")
    end = datetime.datetime.strptime(request["end_date"].split("T")[0], "%Y-%m-%d")
    try:
        df = get_ohlcv(request["symbols"], start, end, request["interval"])
    except MissingDataError:
        download(
            request["provider"], request["symbols"], request["interval"], start, end
        )
        df = get_ohlcv(request["symbols"], start, end, request["interval"])
    env = FullPositionEnv(request, request["symbols"], df, db)
    check_env(env)
    agent = DQNAgent(env)

    return agent, env
