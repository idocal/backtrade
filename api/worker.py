from agents import StatusCallbackDB
from api.db.database import SessionLocal
from api.routers.utils import initialize_agent_env

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
