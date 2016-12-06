import numpy
import math
import random


class Delay(object):
    def __init__(self, num, t):
        self.num = num
        self.id = range(num)
        self.u = [0] * num
        self.n = [0] * num
        self.r = [0] * num
        self.v = 0
        self.T = t
        self.l = 0.0005
        self.TLV = 0.0001
        self.b = 0
        self.o = 0
        self.t_c = 0
        pass

    def set_u(self, u):
        self.u = u
        for i in self.id:
            self.n[i] = 0.01 * random.uniform(0.5, 2)
            self.r[i] = 0.02 * random.uniform(1, 2.5)
        self.v = 50 * random.uniform(0.6, 0.8)

    def con(self):
        m_u = numpy.mean(self.u)
        b = 1.0 * m_u / (m_u + self.v)
        o = 1.0 * self.v / (m_u + self.v)
        t_c = self.T
        t_w = self.num * m_u * self.T / (self.num * m_u + self.v)
        self.b = b
        self.o = o
        self.t_c = t_c
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
        self.b = b
        self.o = o
        self.t_c = t_c
        return b, o, t_c, t_w
        pass

    def df(self, d, i, t):
        n = self.n[i]
        u = self.u[i]
        r = self.r[i]
        d1 = (2 * d + u * r) ** 2
        d2 = 1 + (4 * d * u * t) / d1
        d3 = -(2 * u * t) / (2 * d + u * r)
        d4 = 1 - math.exp(d3) * d2
        return (1 - n) * d4 / t * self.l

    def f(self, d, i, t):
        u = self.u[i]
        r = self.r[i]
        n = self.n[i]
        d1 = -(2 * u * t) / (2 * d + u * r)
        d2 = 1 - math.exp(d1)
        d3 = (1 - n) * d2
        return d * d3, d * n, (1 - n) * d * math.exp(d1)

    def good(self, l, t_c):
        o = [0] * self.num
        m = []
        for i in self.id:
            a, b, c = self.f(l[i], i, t_c)
            o[i] = a
            m.append((i, b, c))
        return o, m

    def gdm(self, d):
        d *= self.t_c
        d_o = d
        k_ori = [d * self.b] * self.num
        d *= self.o
        dfa = [0] * self.num
        s = -1
        while True:
            if d <= 0 or s == 0:
                break
            for i in self.id:
                dfa[i] = self.df(k_ori[i], i, self.t_c)
                if dfa[i] < self.TLV or dfa[i] > self.u[i] * (2 * self.t_c - self.r[i]) / 2 - k_ori[i]:
                    dfa[i] = 0
            s = sum(dfa)
            if s < d:
                for i in self.id:
                    k_ori[i] += dfa[i]
                d -= s
            else:
                for i in self.id:
                    k_ori[i] += d / s * dfa[i]
                d = 0
        o, m = self.good(k_ori, self.t_c)
        pr = []
        for i in self.id:
            pr.append(round(self.u[i], 4))
            pr.append(round(k_ori[i] / self.t_c, 4))
            pr.append(round(o[i] / self.t_c, 4))
            pr.append(round(m[i][1] / k_ori[i], 4))
            pr.append(round(m[i][2] / k_ori[i], 4))
            a = (sum(o) - o[i] - (self.num - 1) * d_o * self.b) * random.uniform(0.9, 1)
            pr.append(round(a / self.t_c, 4))
            pr.append(round((o[i] + a) / self.t_c, 4))
            pr.append(round((d_o - o[i] - a) / d_o, 4))
            # break
        # band Mbps, c_rate Mbps, c_good Mbps, c_loss_tran, c_loss_time, w_rate Mbps, all Mbps, loss Mbps
        return pr


def ran():
    m = random.uniform(600, 1100)
    m *= 8.0 / 1024
    return m
    pass


if __name__ == '__main__':
    dd = Delay(3, 0.25)
    for ii in range(1000):
        dd.set_u([ran(), ran(), ran()])
        dd.con()
        print ii, dd.gdm(3.0)
    pass
    # 250*4=1000
