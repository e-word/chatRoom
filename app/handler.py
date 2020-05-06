#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
import logging
import sys
import datetime
import json

clients = dict()

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=LOG_FORMAT)


class ChatHandler(WebSocketHandler):
    def open(self):
        # 获取客户端IP信息
        self.id = self.request.remote_ip
        # 如果链接加入,
        clients[self.id] = {"id": self.id, "object": self}
        logging.info("客户端[%s]加入聊天室", self.request.remote_ip)
        # 消息通知各个客户端,某个IP客户端加入聊天室
        for client in clients.values():
            client['object'].write_message(self.package_message(client["id"], "login", "客户端[%s]登录聊天室" % self.id))
        pass

    # 处理接收的消息
    def on_message(self, data):
        logging.info("客户端[%s]说[%s]", self.request.remote_ip, data)
        # 服务端接受到消息,转发消息到其余客户端
        for client in clients.values():
            client['object'].write_message(self.package_message(client["id"], "chat", data))
        pass

    def data_received(self, chunk: bytes):
        print(str(chunk, encoding="utf-8"))
        pass

    def on_close(self):
        if self.id in clients:
            del clients[self.id]
            # 消息通知各个客户端,某个IP客户端加入聊天室
        for client in clients.values():
            client['object'].write_message(self.package_message(client["id"], "logout", "客户端[%s]退出聊天室" % self.id))
        pass

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求

    # 通信消息组装
    def package_message(self, ip, type, content):
        message = dict()
        message["type"] = type
        message["ip"] = self.id
        message["time"] = datetime.datetime.now().strftime("%H:%M:%S")
        message["text"] = content
        message["mine"] = self.id == ip
        return message


class IndexHandler(RequestHandler):
    def get(self):
        self.render("index.html")
