import argparse

import logging
logger=logging.getLogger(__name__)
del(logging)

from tornado.web import Application
from tornado.ioloop import IOLoop
from websocketrpc.protocol import Protocol

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

    def send_reply(self, return_code, request, result):
        assert 0
        request.ws_connection.write_message(json.dumps([return_code, request.call_id, result])) # TODO: only one json.dumps() in code.

    def on_message(self, message):
        'Server: message is function call'
        if message is None:
            # happens on close: TODO: needed?
            return
        try:
            func_str, cls, call_id, data = self.deserialize(message)            
        except ValueError, exc:
            msg='Protocol Error: %s' % exc
            logger.warn(msg)
            return

        assert cls in [CLS_REQUEST]
        request=ServerRequest(func_str, call_id, data, self.ws_connection)

        logger.info('received %r' % request)
            
        if not request.func_str in self.funcs:
            return self.send_reply(ServerReplyExc(request, 'Unknown Method %r' % request.func_str))

        func=getattr(self, request.func_str, None)
        if func is None:
            logger.warn('%s unknown' % request.func_str)
            return self.send_exc(request, 'Unknown Method: %s' % request.func_str)
        try:
            result=func(request)
        except Exception, exc:
            return self.send_exc(request, unicode(exc))
        request.finish(self, result)
