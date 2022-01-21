from agents.train import *
from data.download import download

from flask import Flask, request, jsonify
from stable_baselines3.common.logger import *
from enum import Enum

app = Flask(__name__)


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


# TODO: might want to remove is_training and leave just training_step
IS_TRAINING_FILE_PATH = "is_training"


@app.route("/is_training")
def is_training():
    return training_status("is_training", IS_TRAINING_FILE_PATH)


TRAINING_STEP_FILE_PATH = "training_step"


@app.route("/training_step")
def training_step():
    return training_status("training_step", TRAINING_STEP_FILE_PATH)


MODEL_FILE_PATH = "model"


@app.route("/train", methods=["POST"])
def train():
    if request.method == "POST":
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
                IsTrainingCallback(TrainingStatus, file_path=IS_TRAINING_FILE_PATH),
                TrainingStepCallback(TrainingStatus, file_path=TRAINING_STEP_FILE_PATH),
            ],
        )
        agent.save(MODEL_FILE_PATH)

    return jsonify(success=True)


@app.route("/test", methods=["POST"])
def test():
    if request.method == "POST":
        test_config = request.get_json()
        test_env = SingleAssetEnv(test_config)
        check_env(test_env)
        obs = test_env.reset()
        agent = SingleDQNAgent(test_env)
        agent.load(MODEL_FILE_PATH)
        num_test_steps = test_config.get("num_steps", np.inf)
        while test_env.step_idx <= num_test_steps:
            action = agent.predict(obs)
            obs, reward, done, info = test_env.step(action)
            if done:
                break

        resp = jsonify(
            balances=agent.env.ledger.balances,
            timestamps=agent.env.ledger.dates,
            candles=agent.env.df.to_json(),
        )
        return resp


app.run(host="127.0.0.1", port=5000)
