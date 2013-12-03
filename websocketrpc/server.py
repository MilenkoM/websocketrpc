import logging
logger=logging.getLogger(__name__)
del(logging)

from pulsar import Queue
from pulsar.apps import wsgi

from tinyrpc.transports import ServerTransport
from tinyrpc.server import RPCServer
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol

class WebSocketServerTransport(ServerTransport):
    def __init__(self, queue_class=Queue):
        self._queue_class = queue_class
        self.messages = queue_class()

from tinyrpc.dispatch import RPCDispatcher

dispatcher = RPCDispatcher()

class AppHandler(wsgi.LazyWsgi): # used to be WebChat

    def __init__(self, name):
        self.name = name
        transport = WebSocketServerTransport(queue_class=Queue)
        rpc_server = RPCServer(
            transport,
            JSONRPCProtocol(),
            dispatcher
            )
        
    def setup(self):
        backend = self.cfg.get('backend_server')
        return wsgi.WsgiHandler([ws.WebSocket('/jsonrpc', MessungWSHandler())])

    @property
    def cfg(self): # TODO: needed?
        '''Get the ``config`` object from the actor.'''
        actor = pulsar.get_actor()
        if actor.is_arbiter():
            actor = actor.get_actor(self.name)
        return actor.cfg

    @dispatcher.public
    def register_client(self, user_id):
        assert 0

def server(name='wsgi'):
    return wsgi.WSGIServer(callable=AppHandler(name), name=name)

def main():
    server().start()
