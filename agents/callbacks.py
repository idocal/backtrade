from stable_baselines3.common.callbacks import BaseCallback
from enum import Enum
from typing import Type, BinaryIO


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
BYTES = 1


class StatusCallback(BaseCallback):
    def __init__(self, indexes: Type[Enum], file_path: str, num_train_steps: int):
        super(StatusCallback, self).__init__()
        self.indexes = indexes
        self.path = file_path
        self.num_train_steps = num_train_steps
        self.fp = open(self.path, "wb")

    def _on_step(self) -> bool:
        write_progress_to_file(self.fp, self.num_timesteps, self.num_train_steps)
        return True

    def _on_training_start(self) -> None:
        pass

    def _on_training_end(self) -> None:
        self.fp.seek(0)
        self.fp.truncate(0)
        self.fp.write(
            self.indexes.DONE.value.to_bytes(BYTES, byteorder="big", signed=False)
        )
        self.fp.flush()
        self.fp.close()


def write_progress_to_file(
    file: BinaryIO, step: int, total_steps: int = 100, truncate: bool = False
):
    progress = int(step * 100 / total_steps)
    file.seek(0)
    if truncate:
        file.truncate(0)
    file.write(progress.to_bytes(BYTES, byteorder="big", signed=False))
    file.flush()
