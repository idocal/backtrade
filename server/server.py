from agents.train import *
from data.download import download
from data.query import MissingData

import pandas as pd
from flask import Flask, request, jsonify, session, Response
from stable_baselines3.common.logger import *

from enum import Enum
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def index():
    return jsonify(alive=True)


class Status(Enum):
    DONE = 0
    DID_NOT_START = -1


MODEL_FILE_PATH = "model"
TRAINING_STATUS_FILE_PATH = "training_status"
TESTING_STATUS_FILE_PATH = "testing_status"


def status(param_name: str, path: str):
    try:
        fp = open(path, "rb")
        st = int.from_bytes(fp.read(), byteorder="big")
        fp.close()
        return jsonify({param_name: st})
    except FileNotFoundError:
        """If haven't trained yet"""
        return jsonify({param_name: Status.DID_NOT_START.value})


@app.route("/training_status")
def training_status():
    return status("training_status", TRAINING_STATUS_FILE_PATH)


@app.route("/testing_status")
def testing_status():
    return status("testing_status", TESTING_STATUS_FILE_PATH)


def initialize_session():
    sess_id = time.time_ns()
    session["sess_id"] = sess_id


@app.route("/train", methods=["POST"])
def train():
    if request.method == "POST":
        initialize_session()
        train_config = request.get_json()
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

        def call_train():
            agent.learn(
                num_train_steps,
                callback=[
                    TrainingStepCallback(
                        Status, TRAINING_STATUS_FILE_PATH, num_train_steps
                    ),
                ],
            )
            agent.save(MODEL_FILE_PATH)

        r = jsonify(id=session["sess_id"])
        r.call_on_close(call_train)
        return r


@app.route("/test", methods=["POST"])
def test():
    if request.method == "POST":
        test_config = request.get_json()
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
            agent.load(MODEL_FILE_PATH)
        except FileNotFoundError:
            return Response(
                "Agent model file not found, try training first.", status=500
            )

        # TODO: respond to client before testing?

        fp = open(TESTING_STATUS_FILE_PATH, "wb")
        while True:
            action = agent.predict(obs)
            obs, reward, done, info = test_env.step(action)
            write_progress_to_file(test_env.step_idx, len(test_env.df), fp)
            if done:
                fp.seek(0)
                fp.truncate(0)
                fp.write(
                    Status.DONE.value.to_bytes(
                        INDEX_BYTES, byteorder="big", signed=False
                    )
                )
                fp.flush()
                fp.close()
                break

        # TODO assert length of ledger and candles is the same (or not)

        def generate_data(df: pd.DataFrame):
            """Yields the whole ledger in one chunk, then yields every candle in order"""

            yield '{"ledger":' + json.dumps(
                dict(
                    balances=agent.env.ledger.balances,
                    timestamps=agent.env.ledger.dates,
                ),
                indent=4,
                sort_keys=True,
                default=str,
            ) + ',"candles":{'
            for i in range(len(df) - 1):
                yield f'"{i}":' + df.iloc[i].to_json(orient="values") + ","
            yield f'"{len(df) - 1}":' + df.iloc[len(df) - 1].to_json(
                orient="values"
            ) + "}}"

        return Response(generate_data(agent.env.df), mimetype="application/json")


app.run(host="127.0.0.1", port=5000)
