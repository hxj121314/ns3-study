#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import os


class proto(object):
    def __init__(self, source, seg_len, tile, svc):
        self._root = os.path.split(os.path.realpath(__file__))[0] + os.sep
        self._source = self._root + 'input' + os.sep + source + '.yuv'
        self._output = self._root + 'output' + os.sep
        self._seg_len = seg_len
        self._tile = tile
        self._svc = svc
        self.check_env()
        pass

    def check_env(self):
        assert os.path.exists(self._source)
        for i in os.listdir(self._output):
            if i[0] != '.':
                os.remove(self._output + i)

    def run(self):
        pass

    def result(self):
        return 123


def main():
    source = 'container_cif'
    seg_len = 10
    tile = (4, 4)
    svc = 3
    p = proto(source, seg_len, tile, svc)
    p.run()
    print p.result()
    pass


if __name__ == '__main__':
    main()
    pass
