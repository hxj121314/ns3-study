import numpy
import math


class delay(object):
    def __init__(self, num, T):
        self.num = num
        self.id = range(num)
        self.u = [0] * num
        self.n = [0.01] * num
        self.r = [0.02] * num
        self.v = 54
        self.T = T
        self.l = 0.05
        self.TLV = 0.01
        pass

    def set_u(self, u):
        self.u = u

    def out(self):
        print 'num', self.num
        print 'id', self.id
        print 'u', self.u
        print 'con', self.con()
        print 'seq', self.seq()
        print 'r', self.r
        print 'n', self.n

    def con(self):
        m_u = numpy.mean(self.u)
        b = 1.0 * m_u / (m_u + self.v)
        o = 1.0 * self.v / (m_u + self.v)
        t_c = self.T
        t_w = self.num * m_u * self.T / (self.num * m_u + self.v)
        return b, o, t_c, t_w
        pass

    def seq(self):
        m_u = numpy.mean(self.u)
        b = 1.0 * (self.num * m_u - self.v) / (self.num * m_u + (self.num - 1) * self.v)
        o = 1.0 * (self.num * self.v) / (self.num * m_u + (self.num - 1) * self.v)
        if b < 0:
            b = 0
            o = 1
        t_c = self.T / 2
        t_w = self.T / 2
        return b, o, t_c, t_w
        pass

    def df(self, d, n, u, t, r):
        d1 = (2 * d + u * r) ** 2
        d2 = 1 + (4 * d * u * t) / d1
        d3 = -(2 * u * t) / (2 * d + u * r)
        d4 = 1 - math.exp(d3) * d2
        return (1 - n) * d4

    def f(self, d, u, t, r, n):
        d1 = -(2 * u * t) / (2 * d + u * r)
        d2 = 1 - math.exp(d1)
        d3 = (1 - n) * d2
        return d * d3

    def good(self, l, t_c):
        o = [0] * self.num
        for i in self.id:
            o[i] = self.f(l[i], self.u[i], t_c, self.r[i], self.n[i])
        return o

    def gdm(self, d, t_c):
        k_ori = [0] * self.num
        dfa = [0] * self.num
        s = -1
        while True:
            if d <= 0 or s == 0:
                break
            for i in self.id:
                dfa[i] = self.df(k_ori[i], self.n[i], self.u[i], t_c, self.r[i])
                if dfa[i] * self.l < self.TLV or dfa[i] * self.l > self.u[i] * (2 * t_c - self.r[i]) / 2 - k_ori[i]:
                    dfa[i] = 0
                    continue
            s = sum(dfa)
            if s < d:
                for i in self.id:
                    k_ori[i] += dfa[i]
                d -= s
            else:
                for i in self.id:
                    k_ori[i] += d / s * dfa[i]
                d = 0
        o = self.good(k_ori, t_c)
        return k_ori, d, o, sum(o)


if __name__ == '__main__':
    d = delay(3, 0.25)
    d.set_u([4.8, 6.4, 6.4])
    d.out()
    print d.gdm(1.8, 0.25)
    pass
