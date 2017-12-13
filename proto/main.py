#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import os
from proto import Proto
from media import *


def test_comp():
    s = 'jWbLLKdO7k4'
    yuv = YUVUtil(s, width=1280, height=720, comp=VmafComp)
    yuv2 = YUVUtil(s, width=1280, height=720)

    enc = YUVEncode(yuv.get_output())
    ret_list = []
    frm = 30
    for i in range(10, 40, 2):
        ret = enc.jm_h264(yuv.get_source(), (1280, 720), rate=i * 100000, f_rate=30, frm=frm)
        size = os.path.getsize(ret)
        size *= 8.0 * (30.0 / frm) / 1000000
        out = enc.jm_yuv(ret, yuv.get_source(), '123.yuv')
        p, s = yuv.comp_yuv(out)
        p2, s2 = yuv2.comp_yuv(out)
        ret_list.append(','.join([str(i) for i in (size, p, s, p2, s2)]) + '\n')
    with open(yuv.get_output() + '123.csv', 'w') as f:
        f.writelines(ret_list)


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
    # p.run()
    # print p.result()


if __name__ == '__main__':
    main()
    test_comp()
    pass
