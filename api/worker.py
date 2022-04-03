from agents import StatusCallbackDB
from api.db import crud
from api.db.database import SessionLocal
from api.routers.utils import initialize_agent_env
from loguru import logger
from celery import Celery, Task

app = Celery(__name__)
app.conf.broker_url = "redis://localhost:6379"
app.conf.result_backend = "redis://localhost:6379"


class DBTask(Task):
    _session = None

    def after_return(self, *args, **kwargs):
        if self._session is not None:
            self._session.close()

    @property
    def session(self):
        if self._session is None:
            self._session = SessionLocal()

        return self._session


@app.task(name="train_task", base=DBTask, bind=True)
def train_task(self, request):
    agent, env = initialize_agent_env(request)
    num_train_steps = len(env.df)
    agent.learn(
        num_train_steps,
        callback=[StatusCallbackDB(self.session, request["agent_id"], num_train_steps)],
    )
    agent.save("models" + "/" + request["agent_id"])
    return


@app.task(name="test_task", base=DBTask, bind=True)
def test_task(self, request):
    agent, env = initialize_agent_env(request)
    agent.load("models" + "/" + request["agent_id"])
    obs = env.reset()
    total_steps = len(env.df)
    crud.delete_balances(self.session, request["agent_id"])
    crud.delete_trades(self.session, request["agent_id"])
    logger.info(f"Testing agent on symbols:{request['symbols']}")
    while True:
        action = agent.predict(obs)
        obs, reward, done, info = env.step(action)
        crud.update_agent(
            self.session,
            request["agent_id"],
            "test_progress",
            env.step_idx / total_steps,
        )
        if done:
            break

    # TODO assert length of ledger and candles is the same (or not)
    logger.info("Saving test results to DB...")
    ledger_data = agent.env.ledger.get_data()
    if ledger_data["trades"]:
        crud.add_trades(
            self.session, request["agent_id"], ledger_data["trades"]
        )
    crud.add_balances(self.session, request["agent_id"], ledger_data)
    crud.update_agent(self.session, request["agent_id"], "test_done", 1)
    return
