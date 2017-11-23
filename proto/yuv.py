#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import numpy as np
from PIL import Image
import subprocess
import os


class YUVUtil(object):
    def __init__(self, name, width=352, height=288):
        self._w = width
        self._h = height
        self._size = (self._w, self._h)
        self._root = os.path.split(os.path.realpath(__file__))[0] + os.sep
        self._source = self._root + 'input' + os.sep + name + '.yuv'
        self._output = self._root + 'output' + os.sep + name + '_'

    def read420(self):
        with open(self._source, 'rb') as f:
            while f.tell() < os.fstat(f.fileno()).st_size:
                y = f.read(self._w * self._h)
                u = f.read(self._w * self._h / 4)
                v = f.read(self._w * self._h / 4)

                y = np.array(bytearray(y), dtype=np.uint8)
                u = np.array(bytearray(u), dtype=np.uint8)
                v = np.array(bytearray(v), dtype=np.uint8)

                y = y.reshape((self._h, self._w))
                u = u.reshape((self._h / 2, self._w / 2))
                v = v.reshape((self._h / 2, self._w / 2))
                assert len(y) == self._h
                assert len(y[0]) == self._w
                yield y, u, v

    def split_ffmpeg_h264(self, source, (w, h), output):
        output = self._output + output
        subprocess.check_output(
            "ffmpeg " +
            " -f rawvideo -pix_fmt yuv420p -s:v " +
            str(w) + "x" + str(h) + " -i " +
            source +
            " -r 25 -c:v libx264 " + output,
            shell=True, stderr=subprocess.STDOUT)
        return output

    def yuv_ffmpeg_h264(self, output='sp.mp4'):
        return self.split_ffmpeg_h264(self._source, self._size, output)

    def comp(self, f1='sp.mp4'):
        f1 = self._output + f1
        subprocess.check_output(
            "ffmpeg -i " +
            f1 +
            " -pix_fmt yuv420p -s " +
            str(self._w) + "x" + str(self._h) + " -i " +
            self._source +
            " -filter_complex \"psnr='stats_file=" + f1 + ".log'\" -f null -",
            shell=True, stderr=subprocess.STDOUT)
        with open(f1 + ".log") as f:
            content = f.readlines()
        return [i.strip() for i in content]

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

    def rgb2img(self, (r, g, b)):
        im_r = Image.frombytes('L', self._size, r.tostring())
        im_g = Image.frombytes('L', self._size, g.tostring())
        im_b = Image.frombytes('L', self._size, b.tostring())
        return Image.merge('RGB', (im_r, im_g, im_b))

    def yuv2img(self, yuv):
        return self.rgb2img(self.yuv2rgb(yuv))

    def yuv_split(self, (y, u, v), (w, h), (off_w, off_h)):
        assert w + off_w <= self._w
        assert h + off_h <= self._h
        u = np.repeat(u, 2, 0)
        u = np.repeat(u, 2, 1)
        v = np.repeat(v, 2, 0)
        v = np.repeat(v, 2, 1)
        y = y[off_h:off_h + h, off_w:off_w + w]
        u = u[off_h:off_h + h, off_w:off_w + w]
        v = v[off_h:off_h + h, off_w:off_w + w]
        u = u[::2, ::2]
        v = v[::2, ::2]
        return y, u, v

    def show_img(self):
        index = 0
        for frm in self.read420():
            co = self.yuv2img(frm)
            co.save(self._output + str(index) + '.jpg')
            index += 1
        return index

    def split_run(self, tmp_size, tmp_off, output='sp.yuv'):
        output = self._output + output
        with open(output, 'wb') as f:
            for frm in self.read420():
                data = self.yuv_split(frm, tmp_size, tmp_off)
                f.write(''.join([i.tostring() for i in data]))
        return output

    def make_tile(self, tile):
        x, y = tile
        w = self._w / x
        h = self._h / y

        x = 0
        y = 0
        for j in range(0, self._h, h):
            for i in range(0, self._w, w):
                ret = self.split_run((w, h), (i, j), "sp_{0}_{1}.yuv".format(x, y))
                self.split_ffmpeg_h264(ret, (w, h), "sp_{0}_{1}.mp4".format(x, y))
                y += 1
            y = 0
            x += 1
        pass
