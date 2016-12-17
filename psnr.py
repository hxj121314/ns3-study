import random
import subprocess
import numpy


def res(name):
    name += '.log'
    re = []
    with open(name) as f:
        al = f.readlines()
    for i in al:
        m = i.split()
        m = m[5].split(':')
        assert 'psnr_avg' == m[0]
        re.append(m[1])
    return re
    pass


def comp(name):
    f1 = name + '_cif.yuv'
    f2 = name + '2.264'
    subprocess.check_output(
        "ffmpeg -i " +
        f2 +
        " -pix_fmt yuv420p -s 352x288 -i " +
        f1 +
        " -filter_complex \"psnr='stats_file=" + name + ".log'\" -f null -",
        shell=True, stderr=subprocess.STDOUT)
    pass


def cond(name, frame, lo, fi):
    iframe = ''
    pframe = ''
    with open(name + '.264') as f:
        for i in range(len(frame)):
            al = f.read(frame[i])
            if i % 5 == 0:
                if i not in lo:
                    iframe = al
                fi.write(iframe)
            else:
                if i not in lo:
                    pframe = al
                fi.write(pframe)
    pass


def loss(frame, rate):
    lo = []
    for i in range(2, len(frame)):
        fr = frame[i]
        if i % 5 == 0:
            fr /= 3 / rate
        mtu = int(fr / 1470) + 1
        lo.extend([i] * mtu)
    rate = int(len(lo) * rate)
    random.shuffle(lo)
    return lo[0:rate]
    pass


def sp(i):
    with open(i + '.txt') as f:
        al = f.readlines()
    frame = []
    for i in al:
        s = i.split()
        l = len(s)
        if l == 10:
            frame.append(int(s[1]) / 8 + 328 / 8)
        elif l == 12:
            frame.append(int(s[3]) / 8)
    return frame
    pass


def main(i, lo):
    lib = ['akiyo', 'coastguard', 'container', 'mobile']
    su = []
    for itera in range(20):
        su.extend(handle(lib[i], lo))
    return su[:5000]


def handle(name, lo):
    frame = sp(name)
    lo = loss(frame, lo)
    with open(name + '2.264', 'w') as f:
        cond(name, frame, lo, f)
    comp(name)
    return res(name)
    pass


def micro():
    rate = [0.2131, 0.0809, 0.26439725, 0.1051, 0.0737]
    i = 3
    for lo in rate:
        su = main(i, lo)
        print '[' + ' '.join(su) + '];'
    pass


def avg():
    # rate = [0.1051, 0.0809, 0.0737]  # cl
    # rate = [0.26439725, 0.2131, 0.0809]  # mu
    rate = [0.0000000001]
    s = []
    for i in range(4):
        for lo in rate:
            su = main(i, lo)
            su = [float(m) for m in su]
            s.append(numpy.mean(su))
            print numpy.mean(su), max(su), min(su)
    print '[' + ' '.join([str(m) for m in s]) + '];'
    pass


if __name__ == '__main__':
    avg()
    pass
# print numpy.mean(su), max(su), min(su), len(su), su
