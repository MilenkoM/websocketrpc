import argparse

import logging
logger = logging.getLogger(__name__)
del(logging)

from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol, JSONRPCErrorResponse


class RPCSocketHandler(WebSocketHandler):
    '''
    This is **not** a singleton. There is an instance for every client.
    '''

    protocol = JSONRPCProtocol()  # one instance is enough.

    # this needs to be implemented by a subclass. Dict: method_string -->
    # Procedure(method_callback)
    procedures = None

    def on_message(self, message):
        json_request = self.protocol.parse_request(message)
        # procedures (dict: sting --> method) must be implemented in a
        # subclass!
        callback = self.procedures.get(json_request.method)
        if callback is None:
            response = json_request.error_respond(
                'Method %r not implemented' %
                json_request.method)
            self.write_message(response.serialize())
            return
        try:
            result = callback(json_request)
        except Exception, exc:
            response = json_request.error_respond(repr(exc))
            self.write_message(response.serialize())
            return
            
        return self.return_result(result, json_request)

    def return_result(self, result, json_request):
        response = json_request.respond(result)
        self.write_message(response.serialize())

class Server(object):

    @classmethod
    def get_argument_parser(cls, name='WebSocketRPC Server'):
        parser = argparse.ArgumentParser(name)
        parser.add_argument('--port', default=8888, type=int)
        return parser

    @classmethod
    def parse_args_and_run(cls):
        parser = cls.get_argument_parser()

        args = parser.parse_args()

        application = Application([
            (r"/", cls, {'args': args}),
        ])

        try:
            application.listen(args.port)
        except Exception as exc:
            raise exc.__class__('%s port: %s' % (exc, args.port))

        IOLoop.instance().start()


class Procedure(object):

    def __init__(self, callback):
        self.callback = callback

    def __call__(self, json_request):
        return self.callback(*json_request.args, **json_request.kwargs)
