import ns.core as core
import ns.network as network
import ns.point_to_point as point_to_point
import ns.wifi as www
import ns.mobility as mob
import ns.csma as ccc
import ns.internet as internet
import ns.applications as app
import numpy


# // Default Network Topology
# //
# //   Wifi 10.1.3.0
# //                 AP
# //  *    *    *    *
# //  |    |    |    |    10.1.1.0
# // n5   n6   n7   n0 -------------- n1   n2   n3   n4
# //                   point-to-point  |    |    |    |
# //                                   ================
# //

class recv(network.Application):
    def __init__(self, soc, nouse=True):
        self.socket = soc
        self.i = 0
        self.nosue = nouse
        self.avgdelay = []
        super(recv, self).__init__()

    def StartApplication(self):
        self.socket.Bind(network.InetSocketAddress(network.Ipv4Address('0.0.0.0'), 9))
        if not self.nosue:
            self.socket.SetRecvCallback(self.recv)
        self.socket.SetAllowBroadcast(True)
        pass

    def recv(self, p):
        a = network.Address()
        while True:
            packet = p.RecvFrom(a)
            if not packet:
                break
            # aa = network.InetSocketAddress.ConvertFrom(a)
            he = app.SeqTsHeader()
            packet.RemoveHeader(he)
            past = he.GetSeq()
            packet.RemoveHeader(he)
            acc = he.GetSeq()
            new = int(core.Simulator.Now().GetSeconds() * 1000) - past
            if new > 250:
                self.i += 1
            self.avgdelay.append(new)
            print self.i, acc, len(self.avgdelay), numpy.mean(self.avgdelay), max(
                self.avgdelay), min(self.avgdelay), (len(self.avgdelay) - self.i) * 1470 * 8 / 1000000.0 / (
                core.Simulator.Now().GetSeconds() - 1)


class send(network.Application):
    def __init__(self, soc, inter, size, nouse=True):
        inter = core.Seconds(size * 8 / 1000.0 / 1000.0 / inter)
        self.soc = soc
        self.inter = inter
        self.mtu = size
        self.acc = 0
        self.past = 0
        self.limit = 250
        self.nouse = nouse
        if nouse:
            self.add = "10.1.3.1"
        else:
            self.add = "10.1.3.2"
            print size / inter.GetSeconds() * 8 / 1000000
        super(send, self).__init__()
        pass

    def StartApplication(self):
        self.soc.Bind(network.InetSocketAddress(network.Ipv4Address('0.0.0.0'), 9))
        self.soc.Connect(network.InetSocketAddress(network.Ipv4Address(self.add), 9))
        self.soc.SetAllowBroadcast(True)
        if self.nouse:
            core.Simulator.Schedule(core.Seconds(0), self.up)
        else:
            core.Simulator.Schedule(core.Seconds(1.0), self.up2)
        pass

    def packet(self):
        self.acc += 1
        a = network.Packet(self.mtu - 12 * 2)
        he = app.SeqTsHeader()
        he.SetSeq(self.acc)
        a.AddHeader(he)
        he.SetSeq(self.past)
        a.AddHeader(he)
        return a

    def up2(self):
        self.past = int(core.Simulator.Now().GetSeconds() * 1000)
        num = 0.25 / self.inter.GetSeconds()
        # num *= 0.6
        for i in range(int(num)):
            a = self.packet()
            self.soc.Send(a)
        core.Simulator.Schedule(core.Seconds(0.25), self.up2)
        pass

    def up(self):
        past = int(core.Simulator.Now().GetSeconds() * 1000)
        if past - self.past > 250:
            self.past = past
        a = self.packet()
        self.soc.Send(a)
        core.Simulator.Schedule(self.inter, self.up)
        pass


def main(li):
    p2pNodes = network.NodeContainer()
    p2pNodes.Create(2)

    pointToPoint = point_to_point.PointToPointHelper()
    pointToPoint.SetDeviceAttribute("DataRate", core.StringValue(str(int(sum([i[0] for i in li]))) + "Mbps"))
    pointToPoint.SetChannelAttribute("Delay", core.StringValue("20ms"))

    p2pDevices = pointToPoint.Install(p2pNodes)

    csmaNodes = network.NodeContainer()
    csmaNodes.Add(p2pNodes.Get(1))
    csmaNodes.Create(3)

    csma = ccc.CsmaHelper()
    csma.SetChannelAttribute("DataRate", core.StringValue("100Mbps"))
    csma.SetChannelAttribute("Delay", core.TimeValue(core.NanoSeconds(6560)))

    csmaDevices = csma.Install(csmaNodes)

    wifiStaNodes = network.NodeContainer()
    wifiStaNodes.Create(3)
    wifiApNode = p2pNodes.Get(0)

    channel = www.YansWifiChannelHelper.Default()
    phy = www.YansWifiPhyHelper.Default()
    phy.SetChannel(channel.Create())

    wifi = www.WifiHelper()
    # wifi.SetRemoteStationManager("ns3::AarfWifiManager")
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager", "DataMode", core.StringValue("OfdmRate54Mbps"))

    mac = www.WifiMacHelper()
    ssid = www.Ssid("ns-3-ssid")

    mac.SetType("ns3::StaWifiMac", "Ssid", www.SsidValue(ssid), "ActiveProbing", core.BooleanValue(False))
    staDevices = wifi.Install(phy, mac, wifiStaNodes)

    mac.SetType("ns3::ApWifiMac", "Ssid", www.SsidValue(ssid))
    apDevices = wifi.Install(phy, mac, wifiApNode)

    mobility = mob.MobilityHelper()
    mobility.SetPositionAllocator("ns3::GridPositionAllocator", "MinX", core.DoubleValue(0.0),
                                  "MinY", core.DoubleValue(0.0), "DeltaX", core.DoubleValue(5.0), "DeltaY",
                                  core.DoubleValue(10.0),
                                  "GridWidth", core.UintegerValue(3), "LayoutType", core.StringValue("RowFirst"))
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility.Install(wifiApNode)
    mobility.Install(wifiStaNodes)

    stack = internet.InternetStackHelper()
    stack.Install(csmaNodes)
    stack.Install(wifiApNode)
    stack.Install(wifiStaNodes)

    address = internet.Ipv4AddressHelper()
    address.SetBase(network.Ipv4Address("10.1.1.0"), network.Ipv4Mask("255.255.255.0"))
    address.Assign(p2pDevices)

    address.SetBase(network.Ipv4Address("10.1.2.0"), network.Ipv4Mask("255.255.255.0"))
    address.Assign(csmaDevices)

    address.SetBase(network.Ipv4Address("10.1.3.0"), network.Ipv4Mask("255.255.255.0"))
    address.Assign(staDevices)
    address.Assign(apDevices)

    client = csmaNodes.Get(0)
    soc = network.Socket.CreateSocket(client, internet.UdpSocketFactory.GetTypeId())
    pre = li[0]
    client.AddApplication(send(soc, pre[0], pre[1], False))
    for i in range(1, 4):
        client = csmaNodes.Get(i)
        soc = network.Socket.CreateSocket(client, internet.UdpSocketFactory.GetTypeId())
        pre = li[i]
        client.AddApplication(send(soc, pre[0], pre[1]))

    client = wifiStaNodes.Get(0)
    soc = network.Socket.CreateSocket(client, internet.UdpSocketFactory.GetTypeId())
    client.AddApplication(recv(soc))
    client = wifiStaNodes.Get(1)
    soc = network.Socket.CreateSocket(client, internet.UdpSocketFactory.GetTypeId())
    client.AddApplication(recv(soc, False))

    internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    core.Simulator.Stop(core.Seconds(3.0))

    # pointToPoint.EnablePcapAll("third")
    # phy.EnablePcapAll("csma")
    # csma.EnablePcapAll("third", True)
    # stack.EnablePcapIpv4All('ics')

    core.Simulator.Run()
    core.Simulator.Destroy()


if __name__ == '__main__':
    main([(6, 1470), (20, 44), (10, 576), (10, 1471)])
