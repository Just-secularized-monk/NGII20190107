#coding=utf-8

from mininet.node import Host

class IPv6Host(Host):

    # 初始化函数
    def __init__(self, name, inNamespace=True, **params):
        Host.__init__(self, name, inNamespace=inNamespace, **params)
        self.exectoken = "/tmp/mn-exec-token-host-%s" % name
        self.cmd("touch %s" % self.exectoken)
    
    # 配置函数
    def config(self, ipv4, ipv6, ipv6_gw=None, ipv4_gw=None, **params):
        r = super(IPv6Host, self).config(**params)
        self.cmd('ip -6 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -6 addr add %s dev %s' % (ipv6, self.defaultIntf()))
        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -4 addr add %s dev %s' % (ipv4, self.defaultIntf()))

	# 关闭网卡功能命令
        for off in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" \
                  % (self.defaultIntf(), off)
            self.cmd(cmd)

        if ipv6_gw:
            self.cmd('ip -6 route add default via %s' % ipv6_gw)

        if ipv4_gw:
            self.cmd('ip -4 route add default via %s' % ipv4_gw)

        def updateIP():
            return ipv6.split('/')[0]
        self.defaultIntf().updateIP = updateIP
        
        return r

    def startIperfServer(self):
        self.cmd(self.getInfiniteCmdBg("iperf -s -u"))
	self.cmd(self.getInfiniteCmdBg("iperf -s -u -V"))
	self.cmd(self.getInfiniteCmdBg("iperf -s -u -V"))
	self.cmd(self.getInfiniteCmdBg("iperf -s -u -V -p 5001"))
	self.cmd(self.getInfiniteCmdBg("iperf -s -u -V -p 5002"))
	self.cmd(self.getInfiniteCmdBg("iperf -s -u -V -p 5003"))

    def stop(self, **kwargs):
        self.cmd("killall iperf")
        self.cmd("killall ping")
        self.cmd("killall arping")

    def describe(self):
        print "**********"
        print self.name
        print "default interface: %s\t%s\t%s" % (
            self.defaultIntf().name,
            self.defaultIntf().IP(),
            self.defaultIntf().MAC()
        )
        print "**********"

    def getInfiniteCmdBg(self, cmd, logfile="/dev/null", delay=1):
        return "(while [ -e {} ]; " \
               "do {}; " \
               "sleep {}; " \
               "done;) > {} 2>&1 &".format(self.exectoken, cmd, delay, logfile)

    # 终止函数
    def terminate(self):
        super(IPv6Host, self).terminate()

