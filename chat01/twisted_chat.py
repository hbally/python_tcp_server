# -*- coding: utf-8 -*-
# @Time    : 2017/11/17 10:45
# @Author  : Ayan
# @Email   : hbally
# @File    : twisted_chat.py
# @Software: PyCharm

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


class Chat(LineReceiver):
    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "GETNAME"

    def connectionMade(self):
        self.sendLine("What's your name?")

    def connectionLost(self, reason):
        if self.name in self.users:
            del self.users[self.name]

    def lineReceived(self, line):
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        else:
            self.handle_CHAT(line)

    def handle_GETNAME(self, name):
        if name in self.users:
            self.sendLine("Name taken, please choose another.")
            return
        self.sendLine("Welcome, %s!" % (name,))
        self.name = name
        self.users[name] = self
        self.state = "CHAT"

    def handle_CHAT(self, message):
        message = "<%s> %s" % (self.name, message)
        for name, protocol in self.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)


class ChatFactory(Factory):
    def __init__(self):
        self.users = {}  # maps user names to Chat instances

    def buildProtocol(self, addr):
        return Chat(self.users)


if __name__ == "__main__":
    reactor.listenTCP(8123, ChatFactory())
    reactor.run()

    # 直接用telnet 127.0.0.1 8123 就可以连接tcp服务了
