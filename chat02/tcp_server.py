# -*- coding: utf-8 -*-
# @Time    : 2017/11/17 11:07
# @Author  : Ayan
# @Email   : hbally
# @File    : tcp_server.py
# @Software: PyCharm

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
import struct
import json
from twisted.python import log
import sys

log.startLogging(sys.stdout)


class Chat(Protocol):
    def __init__(self, users):
        self.users = users
        self.phone_number = None
        self.state = "VERIFY"
        self.version = 0
        self.command_func_dict = {
            1: self.handle_verify,
            2: self.handle_single_chat,
            3: self.handle_group_chat,
            4: self.handle_broadcast_chat
        }

    def connectionMade(self):
        log.msg("New connection, the info is:", self.transport.getPeer())

    def connectionLost(self, reason):
        if self.phone_number in self.users:
            del self.users[self.phone_number]

    def dataReceived(self, data):
        """
        接受到数据以后的操作
        """
        #解包规则unpack提取头‘!3I’导致
        length, self.version, command_id = struct.unpack('!3I', data[:12])
        content = data[12:length]

        if command_id not in [1, 2, 3, 4]:
            return

        if self.state == "VERIFY" and command_id == 1:
            self.handle_verify(content)
        else:
            self.handle_data(command_id, content)

    def handle_verify(self, content):
        """
        验证函数
        """
        content = json.loads(content)
        phone_number = content.get('phone_number')
        if phone_number in self.users:
            log.msg("电话号码<%s>存在老的连接." % phone_number.encode('utf-8'))
            self.users[phone_number].connectionLost("")
        log.msg("欢迎, %s!" % (phone_number.encode('utf-8'),))
        self.phone_number = phone_number
        self.users[phone_number] = self
        self.state = "DATA"

        send_content = json.dumps({'code': 1})

        self.send_content(send_content, 101, [phone_number])

    def handle_data(self, command_id, content):
        """
        根据command_id来分配函数
        """
        self.command_func_dict[command_id](content)

    def handle_single_chat(self, content):
        """
        单播
        """
        content = json.loads(content)
        chat_from = content.get('chat_from')
        chat_to = content.get('chat_to')
        chat_content = content.get('chat_content')
        send_content = json.dumps(dict(chat_from=chat_from, chat_content=chat_content))

        self.send_content(send_content, 102, [chat_to])

    def handle_group_chat(self, content):
        """
        组播
        """
        content = json.loads(content)
        chat_from = content.get('chat_from')
        chat_to = content.get('chat_to')
        chat_content = content.get('chat_content')
        send_content = json.dumps(dict(chat_from=chat_from, chat_content=chat_content))

        phone_numbers = chat_to
        self.send_content(send_content, 103, phone_numbers)

    def handle_broadcast_chat(self, content):
        """
        广播
        """
        content = json.loads(content)
        chat_from = content.get('chat_from')
        chat_content = content.get('chat_content')
        send_content = json.dumps(dict(chat_from=chat_from, chat_content=chat_content))

        phone_numbers = self.users.keys()
        self.send_content(send_content, 104, phone_numbers)

    def send_content(self, send_content, command_id, phone_numbers):
        """
        发送函数
        """
        length = 12 + len(send_content)
        version = self.version
        command_id = command_id
        header = [length, version, command_id]
        header_pack = struct.pack('!3I', *header)
        for phone_number in phone_numbers:
            if phone_number in self.users.keys():
                self.users[phone_number].transport.write(header_pack + send_content)
            else:
                log.msg("Phone_number:%s 不在线,不能聊天." % phone_number.encode('utf-8'))


class ChatFactory(Factory):
    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return Chat(self.users)


if __name__ == "__main__":
    reactor.listenTCP(8124, ChatFactory())
    reactor.run()
