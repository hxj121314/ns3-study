import random


class User(object):
    def __init__(self, size):
        self._k = 1024 * 8
        self._m = self._k * 1024
        self._w, self._h = size
        self._layer = 3
        self._choice = None
        pass

    def get_lte(self):
        return random.normalvariate(1.3 * self._m, 0.6 * self._m)

    def get_view(self):
        self._choice = random.randint(0, self._w - 1), random.randint(0, self._h - 1)
        return self._choice

    def get_exp(self, down, seg):
        view = '{0}-{1}-{2}-{3}'
        x, y = self._choice
        ret = None
        for i in range(0, self._layer):
            needle = view.format(seg, x, y, i)
            if needle in down:
                ret = needle
            else:
                print needle
                break
        return ret


class Sim(object):
    def __init__(self, q, a, size, user):
        self._q = q
        self._a = a
        self._w, self._h = size
        self._layer = 3
        self._user = []
        for i in range(user):
            self._user.append(User(size))
        pass

    def _view(self, user, seg=0):
        x, y = user.get_view()
        data = ['{0}-{1}-{2}-{3}'.format(seg, x, y, i) for i in range(1, self._layer)]
        for x in range(self._w):
            for y in range(self._h):
                data.append('{0}-{1}-{2}-{3}'.format(seg, x, y, 0))
        return data

    def _sort(self, seg=0):
        data = {}
        for i in self._user:
            for j in self._view(i, seg):
                if j in data:
                    data[j] += 1
                else:
                    data[j] = 1
        data = sorted(data.iteritems(), key=lambda (k, v): (v, k), reverse=True)
        return data

    def desc(self, name):
        if name is None:
            return 0, 0
        name = tuple([int(i) for i in name.split('-')])
        seg, x, y, l = name
        q = self._q[seg, x, y, l]
        a = self._a[seg, x, y, l]
        return q, a

    def run(self, seg=0):
        data = self._sort(seg)
        band = 0
        for i in self._user:
            band += i.get_lte()
        ret = []
        for i in data:
            q, a = self.desc(i[0])
            if a < band:
                ret.append(i[0])
                band -= a
        data = []
        for i in self._user:
            m = i.get_exp(ret, seg)
            data.append(self.desc(m)[0])
        return data
