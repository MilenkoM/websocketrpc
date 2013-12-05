import logging
logger=logging.getLogger(__name__)
del(logging)

import pulsar
from pulsar import Queue
from pulsar.apps import wsgi, ws

from tinyrpc.dispatch import RPCDispatcher
from tinyrpc.transports import ServerTransport
from tinyrpc.server import RPCServer
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol

dispatcher = RPCDispatcher()

@dispatcher.public
def reverse_string(s):
    return s[::-1]

class WebSocketServerTransport(ServerTransport): # tinyrpc
    def __init__(self, websocket):
        self.websocket=websocket

    def receive_message(self):
        '''
        called from rpc_server.server_forever(). Blocks until data available.
        We don't block, we receive events.
        returns (context, message)
        '''
        raise NotImplementedError()
    
    def handle_message(self):
        '''
        Copy
        '''

    def send_reply(self, context, reply):
        print 'send_reply', repr(reply)
        self.websocket.write(reply)

class WebSocketRPCServer(RPCServer): # tinyrpc
    def server_forever(self):
        # not used
        while True:
            self.receive_one_message()
            
    def receive_one_message(self):
        # not used
        # copied from RPCServer.server_forever(). https://github.com/mbr/tinyrpc/pull/9
        context, message = self.transport.receive_message()
        return self.handle_message(context, message)
    
    def handle_one_message(self, context, message):
        # assuming protocol is threadsafe and dispatcher is theadsafe, as
        # long as its immutable

        def handle_message(context, message):
            try:
                request = self.protocol.parse_request(message)
            except RPCError as e:
                response = e.error_respond()
            else:
                response = self.dispatcher.dispatch(request)

            # send reply
            self.transport.send_reply(context, response.serialize())

        self._spawn(handle_message, context, message)

class Context(object):
    pass

class WebSocketServer(ws.WS): # pulsar
    def on_open(self, websocket): # from ws.WS
        print 'on_open', websocket, id(websocket)
        websocket.rpc_server=WebSocketRPCServer(
            WebSocketServerTransport(websocket),
            JSONRPCProtocol(),
            dispatcher
            )

    def on_message(self, websocket, message): # from ws.WS
        print 'on_message', websocket, id(websocket), repr(message)
        websocket.rpc_server.handle_one_message(Context(), message)
        
class Site(wsgi.LazyWsgi):

    def setup(self):
        return wsgi.WsgiHandler([ws.WebSocket('/jsonrpc', WebSocketServer())])

    def register_client(self, user_id):
        assert 0

def server(**kwargs):
    return wsgi.WSGIServer(callable=Site(), **kwargs)

def main():
    server().start()
