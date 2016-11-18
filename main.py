import sys
import ns.applications as app
import ns.core as core
import ns.internet as internet
import ns.network as network
import ns.point_to_point
import ns.mobility as mobility
import ns.wifi as wifi


class aaa(network.Application):
    def __init__(self, soc, i):
        self.socket = soc
        self.i = i
        super(aaa, self).__init__()

    def StartApplication(self):
        self.socket.Bind(network.InetSocketAddress(network.Ipv4Address('0.0.0.0'), 9))
        self.socket.Connect(network.InetSocketAddress(network.Ipv4Address('192.168.0.255'), 9))
        self.socket.SetRecvCallback(self.recv)
        self.socket.SetAllowBroadcast(True)
        self.send()
        pass

    def send(self):
        a = network.Packet(1472-8-4)
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


# core.LogComponentEnable("UdpEchoClientApplication", core.LOG_LEVEL_INFO)

wifihelper = wifi.WifiHelper.Default()
wifihelper.SetStandard(wifi.WIFI_PHY_STANDARD_80211a)

wifiphy = wifi.YansWifiPhyHelper.Default()
wifichannel = wifi.YansWifiChannelHelper.Default()
wifiphy.SetChannel(wifichannel.Create())

wifimac = wifi.WifiMacHelper()
wifimac.SetType("ns3::AdhocWifiMac")
wifihelper.SetRemoteStationManager("ns3::ConstantRateWifiManager", "DataMode", core.StringValue("OfdmRate54Mbps"))

stas = network.NodeContainer()
stas.Create(3)

mob = mobility.MobilityHelper()
mob.Install(stas)

stack = internet.InternetStackHelper()
stack.Install(stas)

dev = wifihelper.Install(wifiphy, wifimac, stas)
ip = internet.Ipv4AddressHelper()
ip.SetBase(network.Ipv4Address('192.168.0.0'), network.Ipv4Mask('255.255.255.0'))
i = ip.Assign(dev)

# cli = app.UdpEchoClientHelper(network.Ipv4Address('192.168.0.255'), 9)
# cli.SetAttribute("PacketSize", core.UintegerValue(1024))
# cli.SetAttribute("MaxPackets", core.UintegerValue(1024))
# cli.SetAttribute("Interval", core.TimeValue(core.Seconds(0.0015)))
# c1 = cli.Install(stas)
for i in range(3):
    soc = network.Socket.CreateSocket(stas.Get(i), internet.UdpSocketFactory.GetTypeId())
    cli = aaa(soc, i)
    stas.Get(i).AddApplication(cli)
# c1.Start(core.Seconds(.0))
# c1.Stop(core.Seconds(10.0))

internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

core.Simulator.Stop(core.Seconds(10.0))

wifiphy.EnablePcapAll('adhoc', True)
stack.EnablePcapIpv4All('ipv4')
core.Simulator.Run()
core.Simulator.Destroy()

sys.exit(0)
