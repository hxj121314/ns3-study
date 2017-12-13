#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import os
from proto import Proto
from media import *


def test_comp():
    s = 'container_cif'
    yuv = YUVUtil(s)

    enc = YUVEncode(yuv.get_output())
    ret = enc.jm_h264('./input/container_cif.yuv', (352, 288))
    print yuv.comp(ret)
    print yuv.comp_yuv()


def test_yuv():
    s = 'container_cif'
    yuv = YUVUtil(s)
    yuv.show_img()

    enc = YUVEncode(yuv.get_output())
    enc.jm_h264('./input/container_cif.yuv', (352, 288))


def test_jsvm():
    s = 'container_cif'
    yuv = YUVUtil(s)
    enc = SVCEncode(yuv.get_output())
    ret = enc.jsvm_h264(os.path.split(os.path.realpath(__file__))[0] + os.sep + 'input/container_cif.yuv', (352, 288))
    enc.de_multiplex(ret)
    ret = enc.merge(l=2)
    yuv.comp_yuv(ret)
    pass


def main():
    source = 'container_cif'
    seg_len = 10
    tile = (4, 4)
    svc = 3
    p = Proto(source, seg_len, tile, svc)
    p.run()
    print p.result()
    pass


if __name__ == '__main__':
    test_comp()
    pass
