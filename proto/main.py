#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import os
from proto import Proto
from media import *


def test_yuv():
    s = 'container_cif'
    yuv = YUVUtil(s)

    tmp_size = (352, 288)
    ret = yuv.split_run(tmp_size, (0, 0))

    enc = YUVEncode(yuv.get_output())
    print enc.ffmpeg_h264(ret, tmp_size, s + '_sp.mp4')
    print yuv.comp('sp.mp4')
    print yuv.yuv_ffmpeg_h264('sp2.mp4')
    print yuv.comp('sp2.mp4')
    print yuv.comp_yuv()
    yuv.show_img()
    enc.jm_h264('./input/container_cif.yuv', (352, 288))

    enc = SVCEncode(yuv.get_output())
    ret = enc.jsvm_h264(os.path.split(os.path.realpath(__file__))[0] + os.sep + 'input/container_cif.yuv', (352, 288))
    enc.demultiplex(ret)
    ret = enc.merge()
    yuv.comp(ret)
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
    test_yuv()
    pass
