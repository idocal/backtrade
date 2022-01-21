from stable_baselines3.common.callbacks import BaseCallback


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


class IsTraining(BaseCallback):
    def __init__(self, path: str):
        super(IsTraining, self).__init__()
        self.path = path

    def _on_step(self) -> bool:
        return True

    def _on_training_start(self) -> None:
        fp = open(self.path, 'wb')
        fp.seek(0)
        fp.write((1).to_bytes(1, byteorder="big", signed=False))
        fp.flush()
        fp.close()

    def _on_training_end(self) -> None:
        fp = open(self.path, 'wb')
        fp.seek(0)
        fp.write((0).to_bytes(1, byteorder="big", signed=False))
        fp.flush()
        fp.close()
