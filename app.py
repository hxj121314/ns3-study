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
        self.mtu = 576
        self.past = 0
        self.task = 0
        super(send, self).__init__()
        pass

    def StartApplication(self):
        self.socket.Bind(network.InetSocketAddress(network.Ipv4Address('0.0.0.0'), 9))
        self.socket.Connect(network.InetSocketAddress(network.Ipv4Address('192.168.0.2'), 9))
        self.socket.SetAllowBroadcast(True)
        # self.socket.SetIpTtl(1)
        # core.Simulator.Schedule(core.Seconds(0), self.up)
        core.Simulator.Schedule(core.Seconds(0), self.send)
        pass

    def packet(self):
        self.acc += 1
        a = network.Packet(self.mtu - 12 * 3)
        he = app.SeqTsHeader()
        he.SetSeq(self.acc)
        a.AddHeader(he)
        he.SetSeq(self.i)
        a.AddHeader(he)
        he.SetSeq(self.past)
        a.AddHeader(he)
        he.SetSeq(self.list[self.i][1])
        a.AddHeader(he)
        return a

    def send(self):
        if self.i >= 1000:
            return
        if self.task <= 0:
            slot = self.T * self.i - core.Simulator.Now().GetSeconds()
            if slot <= 0:
                slot = 0
            core.Simulator.Schedule(core.Seconds(slot), self.up)
            return
        a = self.packet()
        self.socket.Send(a)
        self.task -= 1
        core.Simulator.Schedule(core.Seconds(self.rate), self.send)
        pass

    def up(self):
        if self.i >= 1000:
            return
        self.rate = self.list[self.i][2]
        self.rate = self.mtu * 8.0 / self.rate / 1024 / 1024
        self.past = int(self.T * self.i * 1000)
        self.task = self.list[self.i][0]
        self.task = self.mtu * 8.0 / self.rate / 1024 / 1024
        self.task = int(1000.0 / self.task)
        cha = self.task - int(1000.0 / self.rate)
        if cha > 0:
            for i in range(cha):
                a = self.packet()
                self.socket.Send(a)
        # core.Simulator.Schedule(core.Seconds(self.T), self.up)
        core.Simulator.Schedule(core.Seconds(0), self.send)
        self.i += 1
        pass


class recv(network.Application):
    def __init__(self, soc):
        self.socket = soc
        self.past = 0
        self.i = 0
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
            base = he.GetSeq()
            packet.RemoveHeader(he)
            t = he.GetSeq()
            packet.RemoveHeader(he)
            i = he.GetSeq()
            packet.RemoveHeader(he)
            acc = he.GetSeq()
            new = core.Simulator.Now().GetSeconds() * 1000
            if int(base + new - t) > 250:
                self.i += 1
                print self.i, int(base + new - t), i, acc
            self.past = new


def install(t, li):
    p2pmac = p2p.PointToPointHelper()
    p2pmac.SetChannelAttribute("Delay", core.TimeValue(core.Seconds(0.02)))
    p2pmac.SetDeviceAttribute("DataRate", core.StringValue("5.5Mbps"))

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
