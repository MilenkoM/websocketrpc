import logging
logger=logging.getLogger(__name__)
del(logging)

import pulsar
from pulsar import Queue
from pulsar.apps import wsgi, ws

class WebSocketServer(ws.WS):
    def on_open(self, websocket): # from ws.WS
        print 'on_open', websocket
        self.messages=Queue()

    def on_message(self, websocket, message): # from ws.WS
        self.messages.put((websocket, message))
        
class Site(wsgi.LazyWsgi):

    def setup(self):
        return wsgi.WsgiHandler([ws.WebSocket('/jsonrpc', WebSocketServer())])

    def register_client(self, user_id):
        assert 0

def server(**kwargs):
    return wsgi.WSGIServer(callable=Site(), **kwargs)

def main():
    server().start()
