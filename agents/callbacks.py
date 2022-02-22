from stable_baselines3.common.callbacks import BaseCallback
from sqlalchemy.orm import Session
from db import crud


class StatusCallbackDB(BaseCallback):
    def __init__(self, db: Session, agent_id: str, num_train_steps: int):
        super(StatusCallbackDB, self).__init__()
        self.db = db
        self.agent_id = agent_id
        self.num_train_steps = num_train_steps

    def _on_step(self) -> bool:
        crud.update_agent(
            self.db,
            self.agent_id,
            "train_progress",
            self.num_timesteps / self.num_train_steps,
        )
        return True

    def _on_training_start(self) -> None:
        crud.update_agent(self.db, self.agent_id, "train_progress", 0)

    def _on_training_end(self) -> None:
        crud.update_agent(self.db, self.agent_id, "train_done", 1)
