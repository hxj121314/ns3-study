import random
import numpy as np
import hashlib
import pickle
import os


class CheckFile(object):
    def __init__(self, name, seg, (w, h), output):
        self._w = w
        self._h = h
        self._seg = seg
        self._layer = 3
        self._name = [name, seg, w, h, self._layer]
        self._name = '-'.join([str(i) for i in self._name])
        tmp = hashlib.md5(self._name).hexdigest()
        print self._name, tmp
        self._name = tmp
        self._output = output + tmp
        self._quality = None
        self._amount = None
        if os.path.exists(self._output):
            with open(self._output) as f:
                self._quality = pickle.load(f)
                self._amount = pickle.load(f)

    def check(self):
        self._get_amount()
        self._get_quality()
        if not os.path.exists(self._output):
            with open(self._output, 'w') as f:
                pickle.dump(self._quality, f)
                pickle.dump(self._amount, f)
        print self._quality.shape
        print self._amount.shape

    def _get_quality(self):
        """
        seg 0-10, tile (0,0)-(4,4), layer 1-3
        """
        if self._quality is not None:
            return self._quality
        ret = np.zeros(self._seg * self._w * self._h * self._layer, dtype=np.float32)
        ret = ret.reshape((self._seg, self._w, self._h, self._layer))
        for seg in range(self._seg):
            for l in range(self._layer):
                for x in range(self._w):
                    for y in range(self._h):
                        ret[seg, x, y, l] = self._get_quality_sim(seg, (x, y), l)
        self._quality = ret
        return self._quality

    def _get_amount(self):
        """
        seg 0-10, tile (0,0)-(4,4), layer 1-3 separate
        """
        if self._amount is not None:
            return self._amount
        ret = np.zeros(self._seg * self._w * self._h * self._layer, dtype=np.float32)
        ret = ret.reshape((self._seg, self._w, self._h, self._layer))
        for seg in range(self._seg):
            for l in range(self._layer):
                for x in range(self._w):
                    for y in range(self._h):
                        ret[seg, x, y, l] = self._get_amount_sim(seg, (x, y), l)
        self._amount = ret
        return self._amount

    def _get_quality_sim(self, seg=0, (w, h)=(0, 0), layer=1):
        return random.normalvariate(38, 1) + (layer - 1) * 2

    def _get_amount_sim(self, seg=0, (w, h)=(0, 0), layer=1):
        k = 1024 * 8
        return random.normalvariate(130 * k, 20 * k) + (layer - 1) * 60 * k
