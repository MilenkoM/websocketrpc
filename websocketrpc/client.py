#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger=logging.getLogger(__name__)

from pulsar import arbiter, Queue
from pulsar.apps.http import HttpClient
from pulsar.apps import ws

from tinyrpc.transports import ClientTransport
from tinyrpc import RPCClient
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.dispatch import RPCDispatcher

dispatcher = RPCDispatcher()

def main():
    logging.basicConfig(level=logging.DEBUG)
    arbiter(start=start).start()

def start(actor):
    client=Client(actor)
    actor.event_loop.call_soon(client.start)
    return actor

class WebSocketClientTransport(ClientTransport, ws.WS):
    ws = None

    def __init__(self):
        self.queue = Queue()

    def get(self): # TODO wann wird das aufgerufen?
        return self.queue.get()

    def on_message(self, ws, message):
        return self.queue.put(message)
        self.ws.write(message)

    def send_message(self, message, expect_reply=True):
        self.ws.write(message)

class Client(object):
    def __init__(self, actor):
        self.actor=actor
        self.http=HttpClient()

    def start(self):
        transport = WebSocketClientTransport()
        transport.ws = yield self.http.get('ws://127.0.0.1:8060/jsonrpc',
                                           websocket_handler=transport).on_headers

        self.rpc_client=RPCClient(
            JSONRPCProtocol(),
            transport)
        self.actor.event_loop.call_soon(self.call_reverse_string)

    def call_reverse_string(self):
        print 'pre call'
        print self.rpc_client.get_proxy().reverse_string('foo')
        print 'post call'
def reverse_string(s):
    return s[::-1]
