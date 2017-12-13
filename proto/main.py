#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import os
from proto import Proto
from media import *


def issue():
    s = 'ref'
    yuv = YUVUtil(s, width=832, height=480, comp=VmafComp)
    yuv2 = YUVUtil(s, width=832, height=480)
    base = './input/dis.yuv'
    p, s = yuv.comp_yuv(base)
    p2, s2 = yuv2.comp_yuv(base)
    print p, p2, s, s2


def test_comp():
    s = 'jWbLLKdO7k4'
    yuv = YUVUtil(s, width=1280, height=720, comp=VmafComp)
    yuv2 = YUVUtil(s, width=1280, height=720)

    enc = YUVEncode(yuv.get_output())
    ret_list = []
    frm = 60
    for i in range(10, 40, 2):
        ret, base = enc.jm_h264(yuv.get_source(), (1280, 720), rate=i * 100000, f_rate=25, frm=frm)
        size = os.path.getsize(ret)
        size *= 8.0 * (25.0 / frm) / 1000000
        p, s = yuv.comp_yuv(base)
        p2, s2 = yuv2.comp_yuv(base)
        ret_list.append(','.join([str(i) for i in (size, p, s, p2, s2)]) + '\n')
        print ret_list[-1]
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
