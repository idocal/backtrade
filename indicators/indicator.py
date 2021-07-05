import numpy as np
from candles import Candles


class Indicator:

    def __init__(self, candles: Candles):
        self.candles = candles

    @property
    def name(self):
        return 'Indicator'

    def indicator(self) -> np.ndarray:
        raise NotImplementedError()
