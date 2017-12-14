#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import subprocess
import os
import time


class YUVEncode(object):
    def __init__(self, output):
        self._output = output
        self._root = os.path.split(os.path.realpath(__file__))[0] + os.sep
        self._lib = self._root + '..' + os.sep + 'lib' + os.sep
        pass

    @staticmethod
    def wait_proc(cmd, log=False):
        std_out = ['*' * 60, cmd]
        sp = subprocess.Popen(
            cmd, stdout=subprocess.PIPE,
            shell=True, stderr=subprocess.STDOUT)
        out = sp.stdout
        rl_list = []
        while sp.poll() is None:
            rl = out.readline()
            if rl == '':
                time.sleep(1)
                continue
            std_out.append(rl.strip())
            rl_list.append(rl.strip())
        std_out.append(cmd)
        std_out.append('#' * 60)
        if log or sp.poll() != 0:
            for i in std_out:
                print i
        assert sp.poll() == 0
        return rl_list

    def ffmpeg_h264(self, source, (w, h), output='sp.264'):
        output = self._output + output
        cmd = "ffmpeg -f rawvideo -pix_fmt yuv420p -s:v {0}x{1} -i {2} -r 25 -c:v libx264 {3} -y"
        cmd = cmd.format(w, h, source, output)
        self.wait_proc(cmd)
        return output

    def ffmpeg_yuv(self, source, output='123.yuv'):
        assert os.path.exists(source)
        output = self._output + output
        cmd = "ffmpeg -i {0} {1} -y"
        cmd = cmd.format(source, output)
        self.wait_proc(cmd)
        return output

    def jm_yuv(self, in_file, ref_file, output):
        assert os.path.exists(in_file)
        assert os.path.exists(ref_file)
        output = self._output + output
        cmd = '-p InputFile={0} -p OutputFile={1} -p RefFile={2}'
        cmd = self._lib + 'ldecod ' + cmd.format(in_file, output, ref_file)
        self.wait_proc(cmd)
        return output

    def jm_h264(self, source, (w, h), output='jm.264', frm=3, gop=6, rate=30000000, f_rate=60):  # 30Mbps
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
        cmd = self._lib + 'lencod ' + cmd.format(
            w, h, w, h, output, None, source, frm, gop, rate, f_rate, stats, rec, leak
        )
        self.wait_proc(cmd, log=True)
        return output, rec
