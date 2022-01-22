from stable_baselines3.common.callbacks import BaseCallback
from enum import Enum
from typing import Type


class ProgressBar(BaseCallback):
    def __init__(self, total_timesteps: int):
        super().__init__()
        self.total_timesteps = int(total_timesteps)
        self.bar_len = 50

    def _on_step(self) -> bool:
        if self.num_timesteps % int(self.total_timesteps / self.bar_len) == 0:
            l = int(self.num_timesteps / self.total_timesteps * self.bar_len)
            print(f"Step {self.num_timesteps}/{self.total_timesteps}:", end="")
            print("[" + "=" * l + " " * (self.bar_len - l) + "]", end="\r")
        return True

    def _on_training_end(self) -> None:
        print(f"Step {self.num_timesteps}/{self.total_timesteps}: DONE")


# note: potential overflow if not used properly
INDEX_BYTES = 1
PROGRESS_BYTES = 1


class TrainingStepCallback(BaseCallback):
    def __init__(self, indexes: Type[Enum], file_path: str, num_train_steps: int):
        super(TrainingStepCallback, self).__init__()
        self.indexes = indexes
        self.path = file_path
        self.num_train_steps = num_train_steps
        self.fp = open(self.path, "wb")

    def _on_step(self) -> bool:
        progress = int(self.num_timesteps * 100 / self.num_train_steps)
        self.fp.seek(0)
        self.fp.write(progress.to_bytes(PROGRESS_BYTES, byteorder="big", signed=False))
        self.fp.flush()
        return True

    def _on_training_start(self) -> None:
        pass

    def _on_training_end(self) -> None:
        self.fp.seek(0)
        self.fp.truncate(0)
        self.fp.write(
            self.indexes.DONE_TRAINING.value.to_bytes(
                INDEX_BYTES, byteorder="big", signed=False
            )
        )
        self.fp.flush()
        self.fp.close()
