import argparse

import logging
logger=logging.getLogger(__name__)
del(logging)

from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from websocketrpc.protocol import Protocol

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol, JSONRPCErrorResponse

class Server(Protocol):
    @classmethod
    def get_argument_parser(cls, name='WebSocketRPC Server'):
        parser=argparse.ArgumentParser(name)
        parser.add_argument('--port', default=8888, type=int)
        return parser

    @classmethod
    def parse_args_and_run(cls):
        parser=cls.get_argument_parser()

        args=parser.parse_args()

        application = Application([
                (r"/", cls, {'args': args}),
                ])

        try:
            application.listen(args.port)
        except Exception, exc:
            raise exc.__class__('%s port: %s' % (exc, args.port))

        IOLoop.instance().start()

class RPCSocketHandler(WebSocketHandler):
    '''
    This is not a singleton. There is an instance for every client.
    '''

    waiters = set()
    cache = []
    cache_size = 200

    protocol=JSONRPCProtocol() # one instance is enough.

    procedures=None # this needs to be implemented by a subclass

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        RPCSocketHandler.waiters.add(self)

    def on_close(self):
        RPCSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        json_request=self.protocol.parse_request(message)
        callback=self.procedures.get(json_request.method)  # procedures (dict: sting --> method) must be implemented in a subclass!
        if callback is None:
            response=json_request.error_respond('Method %s not implemented' % json_request.method)
        else:
            result=callback(*json_request.args, **json_request.kwargs)
            response=json_request.respond(result)
        self.write_message(response.serialize())
