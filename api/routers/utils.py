from .request_template import RunRequest
from data.query import get_ohlcv
from data.query import MissingDataError
from data.download import download
from envs.SingleAssetEnv import SingleAssetEnv
from agents.SingleDQNAgent import SingleDQNAgent

from stable_baselines3.common.env_checker import check_env


def initialize_agent_env(request: RunRequest):
    try:
        df = get_ohlcv(request.symbol, request.start, request.end, request.interval)
    except MissingDataError:
        download(
            request.provider,
            request.symbol,
            request.interval,
            request.start,
            request.end,
        )
        df = get_ohlcv(request.symbol, request.start, request.end, request.interval)
    env = SingleAssetEnv(request.dict(), df)
    check_env(env)
    agent = SingleDQNAgent(env)

    return agent, env