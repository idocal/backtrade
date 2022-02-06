from agents.callbacks import StatusCallback, write_progress_to_file
from agents.SingleDQNAgent import SingleDQNAgent
from envs.SingleAssetEnv import SingleAssetEnv
from stable_baselines3.common.env_checker import check_env

from data.download import download
from data.query import MissingData

from pandas import DataFrame
from flask import Flask, request, jsonify, Response
from pathlib import Path
from shutil import rmtree
from enum import Enum
from json import dumps
from os import urandom


app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(alive=True)


@app.route("/agent_id")
def agent_id():
    return jsonify(agent_id=int.from_bytes(urandom(24), byteorder='big'))


@app.route("/clear_agent", methods=["POST"])
def clear_agent():
    if request.method == "POST":
        agent_id = request.get_json()["agent_id"]
        rmtree(str(agent_id))
        return jsonify(agent_id=agent_id)


class Status(Enum):
    DONE = 200
    DID_NOT_START = -1


MODEL_FILE_PATH = "model"
TRAIN_STATUS_FILE_PATH = "train_status"
TEST_STATUS_FILE_PATH = "test_status"


def get_status(param_name: str, path: str):
    try:
        fp = open(path, "rb")
        st = int.from_bytes(fp.read(), byteorder="big")
        fp.close()
        complete = True if st == Status.DONE.value else False
        return jsonify({param_name: st, "complete": complete})
    except FileNotFoundError:
        """If haven't trained yet"""
        return jsonify({param_name: Status.DID_NOT_START.value, "complete": False})


@app.route("/train_status", methods=["POST"])
def train_status():
    if request.method == "POST":
        agent_id = request.get_json()["agent_id"]
        return get_status(
            "train_status", str(agent_id) + "/" + TRAIN_STATUS_FILE_PATH
        )


@app.route("/test_status", methods=["POST"])
def test_status():
    if request.method == "POST":
        agent_id = request.get_json()["agent_id"]
        return get_status(
            "test_status", str(agent_id) + "/" + TEST_STATUS_FILE_PATH
        )


@app.route("/train", methods=["POST"])
def train():
    if request.method == "POST":
        train_config = request.get_json()
        agent_id = train_config["agent_id"]
        try:
            env = SingleAssetEnv(train_config)
        except MissingData:
            download(
                [train_config["symbol"]],
                [train_config["interval"]],
                train_config["start"],
                train_config["end"],
            )
            env = SingleAssetEnv(train_config)
        check_env(env)
        agent = SingleDQNAgent(env)
        num_train_steps = len(env.df)
        Path(str(agent_id)).mkdir(exist_ok=True)

        def call_train():
            agent.learn(
                num_train_steps,
                callback=[
                    StatusCallback(
                        Status,
                        str(agent_id) + "/" + TRAIN_STATUS_FILE_PATH,
                        num_train_steps,
                    ),
                ],
            )
            agent.save(str(agent_id) + "/" + MODEL_FILE_PATH)

        r = jsonify(id=agent_id)
        r.call_on_close(call_train)
        return r


@app.route("/test", methods=["POST"])
def test():
    if request.method == "POST":
        test_config = request.get_json()
        agent_id = test_config["agent_id"]
        try:
            test_env = SingleAssetEnv(test_config)
        except MissingData:
            download(
                [test_config["symbol"]],
                [test_config["interval"]],
                test_config["start"],
                test_config["end"],
            )
            test_env = SingleAssetEnv(test_config)
        check_env(test_env)
        obs = test_env.reset()
        agent = SingleDQNAgent(test_env)
        try:
            agent.load(str(agent_id) + "/" + MODEL_FILE_PATH)
        except FileNotFoundError:
            return Response(
                "Agent model file not found, try train first.", status=500
            )

        # TODO: respond to client before test?

        fp = open(str(agent_id) + "/" + TEST_STATUS_FILE_PATH, "wb")
        while True:
            action = agent.predict(obs)
            obs, reward, done, info = test_env.step(action)
            write_progress_to_file(fp, test_env.step_idx, len(test_env.df))
            if done:
                write_progress_to_file(fp, Status.DONE.value)
                fp.close()
                break

        # TODO assert length of ledger and candles is the same (or not)

        def generate_data(df: DataFrame):
            """Yields the whole ledger in one chunk, then yields every candle in order"""

            yield '{"ledger":' + dumps(
                dict(
                    balances=agent.env.ledger.balances,
                    timestamps=agent.env.ledger.dates,
                ),
                indent=4,
                default=str,
            ) + ',"candles":{'
            for i in range(len(df) - 1):
                yield f'"{i}":' + df.iloc[i].to_json(orient="values") + ","
            yield f'"{len(df) - 1}":' + df.iloc[len(df) - 1].to_json(
                orient="values"
            ) + "}}"

        return Response(generate_data(agent.env.df), mimetype="application/json")


app.run(host="127.0.0.1", port=5000)
