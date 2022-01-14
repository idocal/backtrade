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
