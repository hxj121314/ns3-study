import random
import numpy as np


class CheckFile(object):
    def __init__(self, seg, (w, h)):
        self._w = w
        self._h = h
        self._seg = seg
        self._layer = 3
        self._quality = None
        self._amount = None

    def check(self):
        self._get_amount()
        self._get_quality()

    def _get_quality(self):
        """
        seg 0-10, tile (0,0)-(4,4), layer 1-3
        """
        ret = np.zeros(self._seg * self._w * self._h * self._layer, dtype=np.float32)
        ret = ret.reshape((self._seg, self._w, self._h, self._layer))
        for seg in range(self._seg):
            for l in range(self._layer):
                for x in range(self._w):
                    for y in range(self._h):
                        ret[seg, x, y, l] = self._get_quality_sim(seg, (x, y), l)
        print ret.shape
        self._quality = ret

    def _get_amount(self):
        """
        seg 0-10, tile (0,0)-(4,4), layer 1-3 separate
        """
        ret = np.zeros(self._seg * self._w * self._h * self._layer, dtype=np.float32)
        ret = ret.reshape((self._seg, self._w, self._h, self._layer))
        for seg in range(self._seg):
            for l in range(self._layer):
                for x in range(self._w):
                    for y in range(self._h):
                        ret[seg, x, y, l] = self._get_amount_sim(seg, (x, y), l)
        print ret.shape
        self._quality = ret

    def _get_quality_sim(self, seg=0, (w, h)=(0, 0), layer=1):
        return random.normalvariate(38, 1) + (layer - 1) * 2

    def _get_amount_sim(self, seg=0, (w, h)=(0, 0), layer=1):
        k = 1024 * 8
        return random.normalvariate(130 * k, 20 * k) + (layer - 1) * 60 * k
