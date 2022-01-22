import pandas as pd

from agents.train import *
from data.download import download

from flask import Flask, request, jsonify, session, Response
from stable_baselines3.common.logger import *
from enum import Enum
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def index():
    return jsonify(alive=True)


class TrainingStatus(Enum):
    STARTED_TRAINING = 1
    DONE_TRAINING = 0
    DID_NOT_START_TRAINING = -1


MODEL_FILE_PATH = "model"
TRAINING_STATUS_FILE_PATH = "training_status"


@app.route("/training_status")
def training_status():
    try:
        fp = open(TRAINING_STATUS_FILE_PATH, "rb")
        status = int.from_bytes(fp.read(), byteorder="big")
        fp.close()
        return jsonify({"training_status": status})
    except FileNotFoundError:
        """If haven't trained yet"""
        return jsonify({"training_status": TrainingStatus.DID_NOT_START_TRAINING.value})


def initialize_session():
    sess_id = time.time_ns()
    session["sess_id"] = sess_id


@app.route("/train", methods=["POST"])
def train():
    if request.method == "POST":
        initialize_session()
        # TODO return OK
        train_config = request.get_json()
        try:
            env = SingleAssetEnv(train_config)
        except AttributeError:  # TODO specify error
            download(
                [train_config["symbol"]],
                [train_config["interval"]],
                train_config["start"],
                train_config["end"],
            )
            env = SingleAssetEnv(train_config)
        check_env(env)
        agent = SingleDQNAgent(env)
        num_train_steps = train_config["num_steps"]
        agent.learn(
            num_train_steps,
            callback=[
                TrainingStepCallback(
                    TrainingStatus, file_path=TRAINING_STATUS_FILE_PATH
                ),
            ],
        )
        agent.save(MODEL_FILE_PATH)

    return jsonify(id=session["sess_id"])


@app.route("/test", methods=["POST"])
def test():
    if request.method == "POST":
        test_config = request.get_json()
        try:
            test_env = SingleAssetEnv(test_config)
        except AttributeError:  # TODO: specify errors
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

        num_test_steps = test_config.get("num_steps", np.inf)
        while test_env.step_idx <= num_test_steps:
            action = agent.predict(obs)
            obs, reward, done, info = test_env.step(action)
            if done:
                break

        # TODO assert length of ledger and candles is the same

        def generate(df: pd.DataFrame):
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

        return Response(generate(agent.env.df), mimetype="application/json")


app.run(host="127.0.0.1", port=5000)
