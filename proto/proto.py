#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import os

from media import *


class ProtoResult(object):
    def __init__(self, **kargs):
        self._data = dict(kargs)
        pass

    def over_item(self, k, v):
        self._data[k] = v

    def __str__(self):
        ret = ''
        for i in sorted(self._data.keys()):
            if i[0] != '_':
                ret += i + ' : ' + str(self._data[i]) + '\n'
        return ret


class Proto(object):
    def __init__(self, source, seg_len, tile, svc):
        self._name = source
        self._root = os.path.split(os.path.realpath(__file__))[0] + os.sep
        self._source = self._root + 'input' + os.sep + source + '.yuv'
        self._output = self._root + 'output' + os.sep
        self._seg_len = seg_len
        self._tile = tile
        self._svc = svc
        self._ret = {}
        self.check_env()
        pass

    def check_env(self):
        assert os.path.exists(self._source)
        for i in os.listdir(self._output):
            if i[0] != '.':
                if not os.path.isdir(self._output + i):
                    os.remove(self._output + i)
                    pass

    def run(self):
        pass

    def result(self):
        ret = ProtoResult(
            src=self._source,
            seg_len=self._seg_len,
            tile=self._tile,
            svc=self._svc
        )
        for i in self._ret.keys():
            ret.over_item(i, self._ret[i])
        return ret
