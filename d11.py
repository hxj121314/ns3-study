from scapy.all import sniff, conf, Dot11

conf.sniff_promisc = True


def pd11(pkt):
    if Dot11 not in pkt:
        print 1
        return
    pkt.sprintf("{Dot11Beacon:%Dot11.addr3%\t%Dot11Beacon.info%\t%PrismHeader.channel%\tDot11Beacon.cap%}")
    pass


def di():
    sniff(count=10, prn=pd11, store=0)
    pass


if __name__ == '__main__':
    di()
