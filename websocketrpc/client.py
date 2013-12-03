#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger=logging.getLogger(__name__)

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from websocketrpc import WebSocketServerTransport
from tinyrpc.dispatch import RPCDispatcher

dispatcher = RPCDispatcher()

def main():
    logging.basicConfig(level=logging.DEBUG)
    transport = WebSocketServerTransport()
    # start wsgi server as a background-greenlet
    wsgi_server = gevent.wsgi.WSGIServer(('127.0.0.1', 5000), transport.handle)
    gevent.spawn(wsgi_server.serve_forever)

    rpc_server = RPCServereWebSocket(
        transport,
        JSONRPCProtocol(),
        dispatcher
        )
    rpc_server.serve_forever()

@dispatcher.public
def reverse_string(s):
    return s[::-1]
