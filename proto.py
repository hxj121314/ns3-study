#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import numpy as np
from PIL import Image
import subprocess
import os


class YUVUtil(object):
    def __init__(self, width=352, height=288):
        self._w = width
        self._h = height
        self._size = (self._w, self._h)

    def read420(self, name):
        with open(name, 'rb') as f:
            while f.tell() < os.fstat(f.fileno()).st_size:
                y = f.read(self._w * self._h)
                u = f.read(self._w * self._h / 4)
                v = f.read(self._w * self._h / 4)

                y = np.array(bytearray(y), dtype=np.uint8)
                u = np.array(bytearray(u), dtype=np.uint8)
                v = np.array(bytearray(v), dtype=np.uint8)

                y = y.reshape((self._w, self._h))
                u = u.reshape((self._w / 2, self._h / 2))
                v = v.reshape((self._w / 2, self._h / 2))
                yield y, u, v

    @staticmethod
    def yuv2h264(name, w, h, output='sp.mp4'):
        if os.path.exists(output):
            os.remove(output)
        subprocess.check_output(
            "ffmpeg " +
            " -f rawvideo -pix_fmt yuv420p -s:v " +
            str(w) + "x" + str(h) + " -i " +
            name +
            " -r 25 -c:v libx264 " + output,
            shell=True, stderr=subprocess.STDOUT)

    @staticmethod
    def comp(f1, f2):
        subprocess.check_output(
            "ffmpeg -i " +
            f2 +
            " -pix_fmt yuv420p -s 352x288 -i " +
            f1 +
            " -filter_complex \"psnr='stats_file=" + f1 + ".log'\" -f null -",
            shell=True, stderr=subprocess.STDOUT)

    @staticmethod
    def yuv2rgb((y, u, v)):
        u = np.repeat(u, 2, 0)
        u = np.repeat(u, 2, 1)
        v = np.repeat(v, 2, 0)
        v = np.repeat(v, 2, 1)
        r = y + 1.14 * (v - 128.0)
        g = y - 0.395 * (u - 128.0) - 0.581 * (v - 128.0)
        b = y + 2.032 * (u - 128.0)
        return r.astype(np.uint8), g.astype(np.uint8), b.astype(np.uint8)

    def rgb2img(self, (r, g, b), size=None):
        if None is size:
            size = self._size
        im_r = Image.frombytes('L', size, r.tostring())
        im_g = Image.frombytes('L', size, g.tostring())
        im_b = Image.frombytes('L', size, b.tostring())
        return Image.merge('RGB', (im_r, im_g, im_b))

    def yuv2img(self, yuv, size=None):
        return self.rgb2img(self.yuv2rgb(yuv), size)

    def yuv_split(self, (y, u, v), w, h, off_w, off_h):
        assert w + off_w <= self._w
        assert h + off_h <= self._h
        u = np.repeat(u, 2, 0)
        u = np.repeat(u, 2, 1)
        v = np.repeat(v, 2, 0)
        v = np.repeat(v, 2, 1)
        y = y[off_w:off_w + w, off_h:off_h + h]
        u = u[off_w:off_w + w, off_h:off_h + h]
        v = v[off_w:off_w + w, off_h:off_h + h]
        u = u[::2, ::2]
        v = v[::2, ::2]
        return y, u, v


def show_img():
    name = 'container_cif'
    util = YUVUtil()
    index = 0
    for frm in util.read420(name + '.yuv'):
        co = util.yuv2img(frm)
        co.save('./yuvlog/' + str(index) + '.jpg')
        index += 1


def split_run():
    name = 'container_cif'
    w = 352
    h = 288
    util = YUVUtil()
    with open(name + '_sp.yuv', 'wb') as f:
        for frm in util.read420(name + '.yuv'):
            data = util.yuv_split(frm, w, h, 0, 0)
            print len(data[0])
            exit()
            f.write(''.join([i.tostring() for i in data]))
    util.yuv2h264(name + '_sp.yuv', w, h)


if __name__ == '__main__':
    split_run()
