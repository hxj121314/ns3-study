#!/usr/bin/env python2.7
#  -*- coding:utf-8 -*-
from proto import Proto


def main():
    source = 'container_cif'
    seg_len = 10
    tile = (4, 4)
    svc = 3
    p = Proto(source, seg_len, tile, svc)
    p.run()
    print p.result()
    pass


if __name__ == '__main__':
    main()
    pass
