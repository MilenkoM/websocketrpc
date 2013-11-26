import argparse

import logging
logger=logging.getLogger(__name__)
del(logging)

from websocketrpc.protocol import Protocol
from tornado.web import Application
from tornado.ioloop import IOLoop

class Server(Protocol):
    FUNC_TEST_EXCEPTION='test_exception'

    funcs=[
        Protocol.OK,
        Protocol.ERROR,
        Protocol.EXC,
        FUNC_TEST_EXCEPTION,
        ]

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

        application.listen(args.port)

        IOLoop.instance().start()
