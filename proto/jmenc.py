#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import subprocess
import os
import time


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