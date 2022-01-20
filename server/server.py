import numpy as np
from flask import Flask, request, jsonify
from agents.train import *

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(success=True)


@app.route("/is_training")
def is_training():
    pass


MODEL_PATH = "model"


@app.route("/train", methods=["POST"])
def train():
    if request.method == "POST":
        train_config = request.get_json()
        env = SingleAssetEnv(train_config)
        check_env(env)
        agent = SingleDQNAgent(env)
        num_train_steps = train_config["num_steps"]
        agent.learn(num_train_steps)
        agent.save(MODEL_PATH)

    return jsonify(success=True)


@app.route("/test", methods=["POST"])
def test():
    if request.method == "POST":
        test_config = request.get_json()
        test_env = SingleAssetEnv(test_config)
        check_env(test_env)
        obs = test_env.reset()
        agent = SingleDQNAgent(test_env)
        agent.load(MODEL_PATH)
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
