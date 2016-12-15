import sys
import ns.applications as app
import ns.core as core
import ns.internet as internet
import ns.network as network
import ns.point_to_point as p2p
import ns.mobility as mobility
import ns.wifi as wifi
import ns.lte as lte


class aaa(network.Application):
    def __init__(self, soc, index):
        self.socket = soc
        self.i = index
        super(aaa, self).__init__()

    def StartApplication(self):
        self.socket.Bind(network.InetSocketAddress(network.Ipv4Address('0.0.0.0'), 9))
        self.socket.Connect(network.InetSocketAddress(network.Ipv4Address('192.168.0.1'), 9))
        self.socket.SetRecvCallback(self.recv)
        self.socket.SetAllowBroadcast(True)
        # self.socket.SetIpTtl(1)
        self.send()
        pass

    def send(self):
        a = network.Packet(1472 - 8 - 4)
        he = app.SeqTsHeader()
        he.SetSeq(self.i)
        a.AddHeader(he)
        self.socket.Send(a)
        core.Simulator.Schedule(core.Seconds(1), self.send)

    def recv(self, p):
        a = network.Address()
        while True:
            packet = p.RecvFrom(a)
            if not packet:
                break
            aa = network.InetSocketAddress.ConvertFrom(a)
            he = app.SeqTsHeader()
            packet.RemoveHeader(he)
            print self.i, aa.GetIpv4(), aa.GetPort(), he.GetSeq()


def main():
    # core.LogComponentEnable("UdpEchoClientApplication", core.LOG_LEVEL_INFO)

    wifihelper = wifi.WifiHelper.Default()
    wifihelper.SetStandard(wifi.WIFI_PHY_STANDARD_80211a)

    wifiphy = wifi.YansWifiPhyHelper.Default()
    wifichannel = wifi.YansWifiChannelHelper.Default()
    wifiphy.SetChannel(wifichannel.Create())

    wifimac = wifi.WifiMacHelper()
    wifimac.SetType("ns3::AdhocWifiMac")
    wifihelper.SetRemoteStationManager("ns3::ConstantRateWifiManager", "DataMode", core.StringValue("OfdmRate54Mbps"))

    p2pmac = p2p.PointToPointHelper()
    p2pmac.SetChannelAttribute("Delay", core.TimeValue(core.NanoSeconds(6560)))
    p2pmac.SetDeviceAttribute("DataRate", core.StringValue("2Mbps"))

    stas = network.NodeContainer()
    stas.Create(3)

    p2ps = network.NodeContainer()
    p2ps.Create(1)

    mob = mobility.MobilityHelper()
    mob.Install(stas)

    stack = internet.InternetStackHelper()
    stack.Install(stas)
    stack.Install(p2ps)

    dev = wifihelper.Install(wifiphy, wifimac, stas)
    p2ps.Add(stas.Get(0))
    dev2 = p2pmac.Install(p2ps)

    ip = internet.Ipv4AddressHelper()
    ip.SetBase(network.Ipv4Address('192.168.0.0'), network.Ipv4Mask('255.255.255.0'))
    ip.Assign(dev)
    ip.SetBase(network.Ipv4Address('192.168.1.0'), network.Ipv4Mask('255.255.255.0'))
    ip.Assign(dev2)

    client = p2ps.Get(0)
    client.AddApplication(aaa(network.Socket.CreateSocket(client, internet.UdpSocketFactory.GetTypeId()), 0))
    for i in range(3):
        client = stas.Get(i)
        client.AddApplication(aaa(network.Socket.CreateSocket(client, internet.UdpSocketFactory.GetTypeId()), i))

    internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    core.Simulator.Stop(core.Seconds(10.0))

    wifiphy.EnablePcapAll('adhoc', True)
    stack.EnablePcapIpv4All('ipv4')
    core.Simulator.Run()
    core.Simulator.Destroy()

    sys.exit(0)


if __name__ == '__main__':
    main()
