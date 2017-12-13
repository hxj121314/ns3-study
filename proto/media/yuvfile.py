#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import numpy as np
from PIL import Image
import os
from jmenc import YUVEncode


class VmafComp(object):
    def __init__(self, enc):
        self._encoder = enc
        self._root = os.path.split(os.path.realpath(__file__))[0] + os.sep
        self._lib = self._root + '..' + os.sep + 'lib' + os.sep

    def comp(self, w, h, source, f1):
        assert os.path.exists(source)
        assert os.path.exists(f1)
        pass

    def comp_yuv(self, w, h, source, f1):
        assert os.path.exists(source)
        assert os.path.exists(f1)
        cmd = self._lib + "psnr yuv420p {2} {3} {0} {1}"
        cmd = cmd.format(w, h, source, f1)
        ret = self._encoder.wait_proc(cmd)
        avg = []
        for i in ret:
            i = i.strip().split()[-1]
            avg.append(float(i))
        avg = np.mean(avg)
        cmd = self._lib + "ssim yuv420p {2} {3} {0} {1}"
        cmd = cmd.format(w, h, source, f1)
        ret = self._encoder.wait_proc(cmd)
        avg2 = []
        for i in ret:
            i = i.strip().split()
            if i[0] == 'ssim:':
                avg2.append(float(i[-1]))
        avg2 = np.mean(avg2)
        return avg, avg2


class FFComp(object):
    def __init__(self, enc):
        self._encoder = enc

    def comp(self, w, h, source, f1):
        assert os.path.exists(source)
        assert os.path.exists(f1)
        cmd = "ffmpeg -i {2} -pix_fmt yuv420p -s {0}x{1} -i {3}" + \
              " -lavfi \"ssim='stats_file={3}_ssim.log';[0:v][1:v]psnr='stats_file={3}_psnr.log'\" -f null -"
        cmd = cmd.format(w, h, source, f1)
        self._encoder.wait_proc(cmd)
        return self.read_log(f1)

    def comp_yuv(self, w, h, source, f1):
        assert os.path.exists(source)
        assert os.path.exists(f1)
        cmd = "ffmpeg -s {0}x{1} -i {2} -s {0}x{1} -i {3}" + \
              " -lavfi \"ssim='stats_file={3}_ssim.log';[0:v][1:v]psnr='stats_file={3}_psnr.log'\" -f null -"
        cmd = cmd.format(w, h, source, f1)
        self._encoder.wait_proc(cmd)
        return self.read_log(f1)

    @staticmethod
    def read_log(f1):
        with open(f1 + "_ssim.log") as f:
            c1 = f.readlines()
        with open(f1 + "_psnr.log") as f:
            c2 = f.readlines()
        ssim, psnr = [float(i.strip().split('All:')[1].split()[0]) for i in c1], \
                     [float(i.strip().split('psnr_y:')[1].split()[0]) for i in c2]
        psnr = np.mean(psnr)
        ssim = np.mean(ssim)
        return psnr, ssim


class YUVUtil(object):
    def __init__(self, name, width=352, height=288, comp=FFComp):
        self._w = width
        self._h = height
        self._size = (self._w, self._h)
        self._root = os.path.split(os.path.realpath(__file__))[0] + os.sep + '..' + os.sep
        if os.path.exists(name):
            self._source = name
            self._output = self._root + 'output' + os.sep + 'default_'
        else:
            self._source = self._root + 'input' + os.sep + name + '.yuv'
            self._output = self._root + 'output' + os.sep + name + '_'
        self._encoder = YUVEncode(self._output)
        self._comp = comp(self._encoder)

    def get_output(self):
        return os.sep.join(self._output.split(os.sep)[:-1]) + os.sep

    def get_source(self):
        return self._source

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

    def yuv_ffmpeg_h264(self, output='sp.264'):
        return self._encoder.ffmpeg_h264(self._source, self._size, output)

    def comp(self, f1='sp.mp4', in_file=None):
        if in_file is None:
            in_file = self._source
        if not os.path.exists(f1):
            f1 = self._output + f1
        return self._comp.comp(self._w, self._h, in_file, f1)

    def comp_yuv(self, f1=None, in_file=None):
        if in_file is None:
            in_file = self._source
        if f1 is None:
            f1 = self._source
        if not os.path.exists(f1):
            f1 = self._output + f1
        return self._comp.comp_yuv(self._w, self._h, in_file, f1)

    def rgb2img(self, (r, g, b)):
        im_r = Image.frombytes('L', self._size, r.tostring())
        im_g = Image.frombytes('L', self._size, g.tostring())
        im_b = Image.frombytes('L', self._size, b.tostring())
        return Image.merge('RGB', (im_r, im_g, im_b))

    def yuv2img(self, (y, u, v)):
        u = np.repeat(u, 2, 0)
        u = np.repeat(u, 2, 1)
        v = np.repeat(v, 2, 0)
        v = np.repeat(v, 2, 1)
        im_r = Image.frombytes('L', self._size, y.tostring())
        im_g = Image.frombytes('L', self._size, u.tostring())
        im_b = Image.frombytes('L', self._size, v.tostring())
        return Image.merge('YCbCr', (im_r, im_g, im_b))

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

    def img2yuv(self):
        pass

    def yuv_merge(self):
        pass

    def show_img(self):
        index = 0
        for frm in self.read420():
            co = self.yuv2img(frm)
            co.save(self._output + str(index) + '.jpg')
            index += 1
        return index

    def split_run(self, tmp_size, tmp_off, output='sp.yuv'):
        output = self._output + output
        if os.path.exists(output):
            return output
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
        data = []
        for j in range(0, self._h, h):
            for i in range(0, self._w, w):
                ret = self.split_run((w, h), (i, j), "sp_{0}_{1}_{2}_{3}.yuv".format(x, y, w, h))
                print 'MAKE', ret
                data.append(ret)
                y += 1
            y = 0
            x += 1
        return data, w, h
