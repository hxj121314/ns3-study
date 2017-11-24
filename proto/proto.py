#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import os
from yuv import YUVUtil, YUVEncode


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
                os.remove(self._output + i)

    def run(self):
        yuv = YUVUtil(self._name)
        enc = YUVEncode(yuv.get_output())
        enc.jm_h264('./input/container_cif.yuv', (352, 288))
        pass

    def _test_yuv(self):
        yuv = YUVUtil(self._name)
        tmp_size = (352, 288)
        ret = yuv.split_run(tmp_size, (0, 0))
        enc = YUVEncode(yuv.get_output())
        self._ret['o'] = enc.ffmpeg_h264(ret, tmp_size, 'sp.mp4')
        self._ret['ret'] = yuv.comp('sp.mp4')
        self._ret['o2'] = yuv.yuv_ffmpeg_h264('sp2.mp4')
        self._ret['ret2'] = yuv.comp('sp2.mp4')
        yuv.show_img()
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
