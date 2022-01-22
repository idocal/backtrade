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


def training_status(param_name: str, file_path: str):
    try:
        fp = open(file_path, "rb")
        status = int.from_bytes(fp.read(), byteorder="big")
        fp.close()
        return jsonify({param_name: status})
    except FileNotFoundError:
        """If haven't trained yet"""
        return jsonify({param_name: TrainingStatus.DID_NOT_START_TRAINING.value})


MODEL_FILE_PATH = "model"
IS_TRAINING_FILE_PATH = "is_training"
TRAINING_STEP_FILE_PATH = "training_step"


@app.route("/is_training")
def is_training():
    return training_status("is_training", IS_TRAINING_FILE_PATH)
    # return training_status("is_training", session["is_training_path"])


@app.route("/training_step")
def training_step():
    return training_status("training_step", TRAINING_STEP_FILE_PATH)
    # return training_status("training_step", session["training_step_path"])


def initialize_session(msg=None):
    sess_id = time.time_ns()

    session["sess_id"] = sess_id
    session["is_training_path"] = IS_TRAINING_FILE_PATH + "_" + str(sess_id)
    session["training_step_path"] = TRAINING_STEP_FILE_PATH + "_" + str(sess_id)
    session["model_path"] = MODEL_FILE_PATH + "_" + str(sess_id)
    # return Response(msg, status=200)


@app.route("/train", methods=["POST"])
def train():
    if request.method == "POST":
        initialize_session()
        train_config = request.get_json()
        try:
            env = SingleAssetEnv(train_config)
        except AttributeError:
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
                # IsTrainingCallback(TrainingStatus, file_path=session["is_training_path"]),
                # TrainingStepCallback(TrainingStatus, file_path=session["training_step_path"]),

                # TODO: might want to remove is_training and leave just training_step
                IsTrainingCallback(TrainingStatus, file_path=IS_TRAINING_FILE_PATH),
                TrainingStepCallback(TrainingStatus, file_path=TRAINING_STEP_FILE_PATH),
            ],
        )
        # agent.save(session["model_path"])
        agent.save(MODEL_FILE_PATH)

    return jsonify(id=session["sess_id"])


@app.route("/test", methods=["POST"])
def test():
    if request.method == "POST":
        test_config = request.get_json()
        try:
            test_env = SingleAssetEnv(test_config)
        except AttributeError:
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
            # agent.load(MODEL_FILE_PATH + "_" + str(test_config["id"]))
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

        def generate(df: pd.DataFrame):
            """Yields the whole ledger in one chunk, then yields every candle in order"""

            yield '{"ledger":'
            yield json.dumps(
                dict(
                    balances=agent.env.ledger.balances,
                    timestamps=agent.env.ledger.dates,
                ),
                indent=4,
                sort_keys=True,
                default=str,
            )
            yield ',"candles":{'
            for i in range(len(df)):
                yield f'"{i}":'
                yield df.iloc[i].to_json()
                if i != len(df) - 1:
                    yield ","
            yield "}}"

        return Response(generate(agent.env.df), mimetype="application/json")


app.run(host="127.0.0.1", port=5000)
