import numpy
import math
import random
import app
import sys
from sympy import *


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
        self.t_w = 0
        self.base = 0
        pass

    def set_u(self, u):
        self.u = u
        for i in self.id:
            self.n[i] = 0.01 * random.uniform(0.5, 1.5)
            self.r[i] = 0.02 * random.uniform(0.5, 1.5)
        self.v = wifi()

    def con(self):
        m_u = numpy.mean(self.u)
        b = 1.0 * m_u / (m_u + self.v)
        o = 1.0 * self.v / (m_u + self.v)
        t_c = self.T
        t_w = self.num * m_u * self.T / (self.num * m_u + self.v)
        self.b = b
        self.o = o
        self.t_c = t_c
        self.t_w = t_w
        self.base = 0  # (t_w / 2) * (self.num - 1) / self.num
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
        d1 = -(2 * u * t) / (2 * d / 2 + u * r)
        d2 = math.exp(d1)
        d3 = (1 - n) * (1 - d2)
        return d * d3, d * n, (1 - n) * d * d2

    def fwifi(self, d, t):
        u = self.v
        n = random.uniform(0.09, 0.06)
        r = 0.001
        d1 = -(2 * u * t) / (2 * d / 2 + u * r)
        d2 = 1 - math.exp(d1)
        d3 = (1 - n) * d2
        return d * d3

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
        if self.num == 1:
            k_ori = [d_o]
        o, m = self.good(k_ori, self.t_c)
        pr = []
        for i in self.id:
            pr.append(round(self.u[i], 4))
            pr.append(round(k_ori[i] / self.t_c, 4))
            pr.append(round(o[i] / self.t_c, 4))
            pr.append(round(m[i][1] / k_ori[i], 4))
            pr.append(round(m[i][2] / k_ori[i], 4))
            a = self.fwifi((sum(o) - o[i]) / (self.b + self.o / self.num) * self.o / self.num, self.t_w)
            pr.append(round(a / self.t_c, 4))
            pr.append(round((o[i] + a) / self.t_c, 4))
            pr.append(round((d_o - o[i] - a) / d_o, 4))
        # band Mbps, c_rate Mbps, c_good Mbps, c_loss_tran, c_loss_time, w_rate Mbps, all Mbps, loss Mbps
        return pr


def ran(devid):
    m = random.uniform(4.8, 8.8)
    return m * (1 - 0.1 * (devid - 1))
    pass


def wifi():
    return random.uniform(11, 8)
    pass


def main():
    dev = 4
    iid = 3
    video = 6.5  # 3.5 4.5 5.5 6.5
    dd = Delay(iid, 0.25)
    li = []
    suulist = []
    for ii in range(400):
        dd.set_u([ran(dev), ran(dev), ran(dev), ran(dev), ran(dev)])
        b, o, t_c, t_w = dd.con()
        m = 0.02 + video * (b + o / iid) * 0.25 / dd.u[0]  # + video * 0.25 * 2 / 3 / v
        suulist.append(m / 2)
        gdm = dd.gdm(video)
        # suulist.append(1 - suu / video)
        # suulist.append(sum([gdm[iii * 8 + 6] for iii in range(iid)]) / iid)
        # li.append((gdm[1] * 0.25, int(dd.base * 1000), gdm[0]))
        # print ii, gdm
    # app.install(0.25, li)
    print numpy.mean(suulist), max(suulist), min(suulist)
    # print '[' + ' '.join([str(iid) for iid in suulist]) + ']'
    pass
    # 100*4=400


def main2():
    dev = 4
    video = 6.5
    su = []
    for ii in range(400):
        w = sum([ran(dev), ran(dev), ran(dev)])
        v = wifi()
        # m = 0.02 + video * 0.25 / 0.99 / w * 3
        m = 0.02 + video * 0.25 / v / 0.9
        su.append(m / 2)
    print numpy.mean(su), max(su), min(su)
    pass


def ddf(d, t, n, u, r, l):
    d1 = (2 * d + u * r) ** 2
    d2 = 1 + (4 * d * u * t) / d1
    d3 = -(2 * u * t) / (2 * d + u * r)
    d4 = 1 - math.exp(d3) * d2
    return (1 - n) * d4 / t * l


def main3():
    udp = []
    for i in range(1000):
        v = wifi()
        w = v * (1 - random.uniform(0.09, 0.06))
        m = random.uniform(v, w)
        udp.append(','.join([str(m) for m in [v, m, w]]) + '\r\n')
    with open('udp.txt', 'w') as f:
        f.writelines(udp)
    pass


def main4():
    l = 0.1
    d1 = 0
    d2 = 0
    t = 0.25
    n1 = 0.01
    n2 = 0.02
    u1 = 6
    u2 = 8
    r1 = 0.02
    r2 = 0.025
    su = []
    for i in range(6):
        print d1, d2
        su.append(d1)
        su.append(d2)
        d1 += ddf(d1, t, n1, u1, r1, l)
        d2 += ddf(d2, t, n2, u2, r2, l)
    print '[' + ' '.join([str(s) for s in su]) + ']'
    pass


def tw():
    init_printing()
    di, b, d, v, rtt, t, u = symbols("di b d v rtt t u")
    tw = t - (1 - b) * d / u
    lam = -2 * v * tw / (2 * (di - b * d) + v * rtt)
    fun = (di - b * d) * (1 - exp(lam * tw))
    ddd = diff(fun, b)
    print latex(ddd)
    print latex(simplify(ddd))


def di():
    init_printing()
    di, n, u, tc, rtt, fi, b, d, v, tw, rttw = symbols("di n u tc rtt fi b d v tw rttw")
    fun = di * (1 - n) * (1 - exp(-2 * u * tc / (2 * di + u * rtt))) - di + (n - 1) * (1 - fi) * (di - b * d) * (
        1 - exp(-2 * v * tw / ((2 * di - b * d) + v * rttw)))
    ddd = diff(fun, di)
    fun2 = (1 - n) * (
        1 - exp(-2 * u * tc / (2 * di + u * rtt)) * (1 + 4 * di * u * tc / ((2 * di + u * rtt) ** 2))) - 1 + (n - 1) * (
        1 - fi) * (1 - exp(-2 * v * tw / (2 * (di - b * d) + v * rttw)) * (
        1 + 4 * (di - b * d) * v * tw / ((2 * (di - b * d) + v * rttw) ** 2)))
    fun3 = ddd - fun2
    print fun3
    print simplify(fun3)


if __name__ == '__main__':
    di()
