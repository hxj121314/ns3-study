import random


class Sim(object):
    def __init__(self, q, a, size):
        self._k = 1024 * 8
        self._m = self._k * 1024
        self._q = q
        self._a = a
        self._w, self._h = size
        self._layer = 3
        self._user = 40
        pass

    def _get_lte(self):
        return random.normalvariate(1.3 * self._m, 0.6 * self._m)

    def _view(self, seg=0):
        x, y = random.randint(0, self._w - 1), random.randint(0, self._h - 1)
        data = ['{0}-{1}-{2}-{3}'.format(seg, x, y, i) for i in range(1, self._layer)]
        for x in range(self._w):
            for y in range(self._h):
                data.append('{0}-{1}-{2}-{3}'.format(seg, x, y, 0))
        return data

    def _sort(self, seg=0):
        data = {}
        for i in range(self._user):
            for j in self._view(seg):
                if j in data:
                    data[j] += 1
                else:
                    data[j] = 1
        data = sorted(data.iteritems(), key=lambda (k, v): (v, k), reverse=True)
        return data

    def desc(self, name):
        name = tuple([int(i) for i in name.split('-')])
        seg, x, y, l = name
        print name
        q = self._q[seg, x, y, l]
        a = self._a[seg, x, y, l]
        return q, a

    def run(self, seg=0):
        data = self._sort(seg)
        band = 0
        for i in range(self._user):
            band += self._get_lte()
        ret = []
        for i in data:
            q, a = self.desc(i[0])
            if a < band:
                ret.append(i)
                band -= a
        print ret
