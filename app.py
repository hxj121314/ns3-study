import random
import ns.applications as app
import ns.core as core
import ns.internet as internet
import ns.network as network
import ns.point_to_point as p2p


class send(network.Application):
    def __init__(self, soc, t, li):
        self.socket = soc
        self.T = t
        self.list = li
        self.i = 0
        self.rate = 0
        self.acc = 0
        super(send, self).__init__()
        pass

    def StartApplication(self):
        self.socket.Bind(network.InetSocketAddress(network.Ipv4Address('0.0.0.0'), 9))
        self.socket.Connect(network.InetSocketAddress(network.Ipv4Address('192.168.0.2'), 9))
        self.socket.SetAllowBroadcast(True)
        # self.socket.SetIpTtl(1)
        core.Simulator.Schedule(core.Seconds(0), self.up)
        # core.Simulator.Schedule(core.Seconds(0), self.send)
        pass

    def packet(self):
        self.acc += 1
        a = network.Packet(1470 - 12 * 3)
        he = app.SeqTsHeader()
        he.SetSeq(self.acc)
        a.AddHeader(he)
        he.SetSeq(self.i)
        a.AddHeader(he)
        he.SetSeq(int(core.Simulator.Now().GetSeconds() * 1000))
        a.AddHeader(he)
        return a

    def send(self):
        if self.i >= 1000:
            return
        a = self.packet()
        self.socket.Send(a)
        core.Simulator.Schedule(core.Seconds(self.rate), self.send)
        pass

    def up(self):
        if self.i >= 1000:
            return
        self.rate = self.list[self.i][0]
        self.rate = 1470 * 8.0 / self.rate / 1024 / 1024
        for i in range(int(1 / self.rate)):
            a = self.packet()
            self.socket.Send(a)
        core.Simulator.Schedule(core.Seconds(self.T), self.up)
        self.i += 1
        pass


class recv(network.Application):
    def __init__(self, soc):
        self.socket = soc
        super(recv, self).__init__()

    def StartApplication(self):
        self.socket.Bind(network.InetSocketAddress(network.Ipv4Address('0.0.0.0'), 9))
        self.socket.Connect(network.InetSocketAddress(network.Ipv4Address('192.168.0.1'), 9))
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
            t = he.GetSeq()
            packet.RemoveHeader(he)
            i = he.GetSeq()
            packet.RemoveHeader(he)
            acc = he.GetSeq()
            print int(core.Simulator.Now().GetSeconds() * 1000 - t), i, acc


def install(t, li):
    p2pmac = p2p.PointToPointHelper()
    p2pmac.SetChannelAttribute("Delay", core.TimeValue(core.Seconds(0.01)))
    p2pmac.SetDeviceAttribute("DataRate", core.StringValue("8Mbps"))

    stas = network.NodeContainer()
    stas.Create(2)

    stack = internet.InternetStackHelper()
    stack.Install(stas)

    dev = p2pmac.Install(stas)

    ip = internet.Ipv4AddressHelper()
    ip.SetBase(network.Ipv4Address('192.168.0.0'), network.Ipv4Mask('255.255.255.0'))
    ip.Assign(dev)

    client = stas.Get(0)
    client.AddApplication(
        send(network.Socket.CreateSocket(client, internet.UdpSocketFactory.GetTypeId()), t, li))
    client = stas.Get(1)
    client.AddApplication(recv(network.Socket.CreateSocket(client, internet.UdpSocketFactory.GetTypeId())))

    internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()
    # core.Simulator.Stop(core.Seconds(10.0))

    stack.EnablePcapIpv4All('ipv4')
    core.Simulator.Run()
    core.Simulator.Destroy()
    pass
