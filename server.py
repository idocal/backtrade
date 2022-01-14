from flask import Flask, render_template, request
from trainer import SingleDQNTrainer
from callbacks import *

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/handle_results", methods=["POST"])
def handle_results():
    form_data = request.form
    return render_template("handle_results.html", form_data=form_data)


@app.route("/train", methods=["GET", "POST"])
def train():
    if request.method == "POST":
        agent = request.form["agent"]
        symbol = request.form["symbol"]
        interval = request.form["interval"]
        start = request.form["start"]
        end = request.form["end"]
        initial_amount = float(request.form["initial_amount"])
        commission = float(request.form["commission"])
        timesteps = int(request.form["timesteps"])

        t = SingleDQNTrainer(symbol, start, end, interval, initial_amount, commission)
        t.train(timesteps, callback=ProgressBar(timesteps))

    return render_template("train.html")


app.run(host="127.0.0.1", port=5000)
