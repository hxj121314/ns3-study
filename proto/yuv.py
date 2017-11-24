#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import numpy as np
from PIL import Image
import subprocess
import os
import time


class YUVUtil(object):
    def __init__(self, name, width=352, height=288):
        self._w = width
        self._h = height
        self._size = (self._w, self._h)
        self._root = os.path.split(os.path.realpath(__file__))[0] + os.sep
        if os.path.exists(name):
            self._source = name
            self._output = self._root + 'output' + os.sep + 'default_'
        else:
            self._source = self._root + 'input' + os.sep + name + '.yuv'
            self._output = self._root + 'output' + os.sep + name + '_'
        self._encoder = YUVEncode(self._output)

    def get_output(self):
        return self._root + 'output' + os.sep

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

    def comp(self, f1='sp.mp4'):
        if not os.path.exists(f1):
            f1 = self._output + f1
        cmd = "ffmpeg -i {2} -pix_fmt yuv420p -s {0}x{1} -i {3}" + \
              " -filter_complex \"psnr='stats_file={2}.log'\" -f null -"
        cmd = cmd.format(self._w, self._h, f1, self._source)
        self._encoder.wait_proc(cmd)
        with open(f1 + ".log") as f:
            content = f.readlines()
        return [i.strip() for i in content]

    def comp_yuv(self, f1=None):
        if f1 is None:
            f1 = self._source
        if not os.path.exists(f1):
            f1 = self._output + f1
        cmd = "ffmpeg -pix_fmt yuv420p -s {0}x{1} -i {2} -pix_fmt yuv420p -s {0}x{1} -i {3}" + \
              " -filter_complex \"psnr='stats_file={2}.log'\" -f null -"
        cmd = cmd.format(self._w, self._h, f1, self._source)
        self._encoder.wait_proc(cmd)
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
                self._encoder.ffmpeg_h264(ret, (w, h), "sp_{0}_{1}.mp4".format(x, y))
                y += 1
            y = 0
            x += 1
        pass


class YUVEncode(object):
    def __init__(self, output):
        self._output = output
        self._root = os.path.split(os.path.realpath(__file__))[0] + os.sep
        pass

    @staticmethod
    def wait_proc(cmd):
        print '*' * 60
        print cmd
        sp = subprocess.Popen(
            cmd, stdout=subprocess.PIPE,
            shell=True, stderr=subprocess.STDOUT)
        out = sp.stdout
        while sp.poll() is None:
            rl = out.readline()
            if rl == '':
                time.sleep(1)
                continue
            print rl.strip()
        print sp.poll()
        print cmd
        print '#' * 60

    def ffmpeg_h264(self, source, (w, h), output='sp.264'):
        output = self._output + output
        cmd = "ffmpeg -f rawvideo -pix_fmt yuv420p -s:v {0}x{1} -i {2} -r 25 -c:v libx264 {3} -y"
        cmd = cmd.format(w, h, source, output)
        self.wait_proc(cmd)
        return output

    def jm_h264(self, source, (w, h), output='jm.264', frm=3, gop=6, rate=30000000, f_rate=60):
        """
        ./lencod.exe 
        -p OutFileMode=0 
        -p InputFile=akiyo_qcif.yuv 
        -p FramesToBeEncoded=30 
        -p NumberBFrames=0 
        -p IDRPeriod=6 
        -p Bitrate=30000000 
        -p RateControlEnable=1 
        -p RCUpdateMode=3 
        -p FrameRate=60
        """
        output = self._output + output
        cmd = '-p SourceWidth={0} -p SourceHeight={1} -p OutputWidth={2} -p OutputHeight={3} ' + \
              '-p OutputFile={4} -p InputFile={6} -p FramesToBeEncoded={7} ' + \
              '-p IDRPeriod={8} -p Bitrate={9} -p FrameRate={10} -p StatsFile={11} -p ReconFile={12} ' \
              '-p LeakyBucketParamFile={13}'
        stats = self._output + 'stats.dat'
        rec = self._output + 'test_rec.yuv'
        leak = self._output + 'leakybucketparam.cfg'
        cmd = self._root + 'lib' + os.sep + 'lencod ' + cmd.format(
            w, h, w, h, output, None, source, frm, gop, rate, f_rate, stats, rec, leak
        )
        self.wait_proc(cmd)
        return output


class SVCEncode(YUVEncode):
    def __init__(self, output):
        super(SVCEncode, self).__init__(output)
        self._lib = self._root + 'lib' + os.sep
        pass

    def jsvm_config(self, source, (w, h), output='jsvm.264', f_rate=60, seg_len=3):
        main = self._output + 'main.cfg'
        l1 = self._output + 'l1.cfg'
        l2 = self._output + 'l2.cfg'
        l3 = self._output + 'l3.cfg'
        output = self._output + output

        temp = """OutputFile {0} # Bitstream file
FrameRate {1} # Maximum frame rate [Hz]
FramesToBeEncoded {2} # Number of frames 
BaseLayerMode 2
IntraPeriod 48 # Intra Period
GOPSize 4 # GOP Size (at maximum frame rate)
SearchMode 4
SearchRange 32
FastBiSearch 1
NumLayers 3
LayerCfg {3}
LayerCfg {4}
LayerCfg {5}
"""
        temp = temp.format(output, f_rate, seg_len, l1, l2, l3)
        with open(main, 'w') as f:
            f.write(temp)
        temp_0 = """InputFile            {0}      # Input  file
SourceWidth          {1}           # Input  frame width
SourceHeight         {2}           # Input  frame height
FrameRateIn          {3}            # Input  frame rate [Hz]
FrameRateOut         {4}            # Output frame rate [Hz]
IDRPeriod           48
""".format(source, w, h, f_rate, f_rate)
        temp_1 = temp_0 + """
QP                  30             # Quantization parameters
MeQP0               30             # QP for mot. est. / mode decision (stage 0)
MeQP1               30             # QP for mot. est. / mode decision (stage 1)
MeQP2               30             # QP for mot. est. / mode decision (stage 2)
MeQP3               30             # QP for mot. est. / mode decision (stage 3)
MeQP4               30             # QP for mot. est. / mode decision (stage 4)
MeQP5               30             # QP for mot. est. / mode decision (stage 5)
"""
        with open(l1, 'w') as f:
            f.write(temp_1)
        temp_2 = temp_0 + """
InterLayerPred      1              # Inter-layer Pred. (0: no, 1: yes, 2:adap.)
QP                  26             # Quantization parameters
MeQP0               26             # QP for mot. est. / mode decision (stage 0)
MeQP1               26             # QP for mot. est. / mode decision (stage 1)
MeQP2               26             # QP for mot. est. / mode decision (stage 2)
MeQP3               26             # QP for mot. est. / mode decision (stage 3)
MeQP4               26             # QP for mot. est. / mode decision (stage 4)
MeQP5               26             # QP for mot. est. / mode decision (stage 5)
"""
        with open(l2, 'w') as f:
            f.write(temp_2)
        temp_3 = temp_0 + """
InterLayerPred      1              # Inter-layer Pred. (0: no, 1: yes, 2:adap.)
QP                  23             # Quantization parameters
MeQP0               23             # QP for mot. est. / mode decision (stage 0)
MeQP1               23             # QP for mot. est. / mode decision (stage 1)
MeQP2               23             # QP for mot. est. / mode decision (stage 2)
MeQP3               23             # QP for mot. est. / mode decision (stage 3)
MeQP4               23             # QP for mot. est. / mode decision (stage 4)
MeQP5               23             # QP for mot. est. / mode decision (stage 5)
"""
        with open(l3, 'w') as f:
            f.write(temp_3)
        return main

    def jsvm_h264(self, source, (w, h), output='jsvm.264', f_rate=60, seg_len=3):
        """
        H264AVCEncoderLibTestStatic -pf config
        """
        cmd = self._lib + 'H264AVCEncoderLibTestStatic -pf ' + self.jsvm_config(source, (w, h), output, f_rate, seg_len)
        self.wait_proc(cmd)
        return self._output + output

    def demultiplex(self, source, output='', seg_len=30000000, f_rate=60):
        output = self._output + output
        cmd = self._lib + 'demultiplex.py {0} {1} {2} {3}'
        cmd = cmd.format(source, seg_len, output, f_rate)
        self.wait_proc(cmd)
        return cmd

    def merge(self, source='jsvm', seg=0, l=3):
        """
        merge 264 init svc...
        H264AVCDecoderLibTestStatic 264 yuv
        """
        source = self._output + source
        cmd = self._lib + 'svc_merge.py '
        cmd += source + '_rec.264 '
        cmd += source + '.init.svc '
        for i in range(l):
            cmd += source + '.seg{0}-L{1}.svc '.format(seg, i)
        self.wait_proc(cmd)
        return source + '_rec.264'
