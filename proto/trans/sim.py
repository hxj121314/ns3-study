import random


class Sim(object):
    def __init__(self):
        self._k = 1024 * 8
        self._m = self._k * 1024
        pass

    def _get_lte(self):
        return random.normalvariate(1.3 * self._m, 0.6 * self._m)
