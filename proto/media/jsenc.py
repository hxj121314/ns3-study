#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
import os
from jmenc import YUVEncode


class SVCEncode(YUVEncode):
    def __init__(self, output):
        super(SVCEncode, self).__init__(output)
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
        assert l > 0
        source = self._output + source
        if l == 3:
            return self.jsvm_decode(source)
        cmd = self._lib + 'svc_merge.py '
        cmd += source + '_rec.264 '
        cmd += source + '.init.svc '
        for i in range(l):
            cmd += source + '.seg{0}-L{1}.svc '.format(seg, i)
        self.wait_proc(cmd)
        return self.jsvm_decode(source + '_rec')

    def jsvm_decode(self, source):
        cmd = self._lib + 'H264AVCDecoderLibTestStatic ' + source + '.264 ' + source + '.yuv '
        try:
            self.wait_proc(cmd)
        except AssertionError:
            pass
        return source + '.yuv'
