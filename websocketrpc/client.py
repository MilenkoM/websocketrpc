# http://www.tornadoweb.org/en/stable/websocket.html#tornado.websocket.WebSocketClientConnection
# Example of websocket_connect https://gist.github.com/fcicq/5328876
import argparse
import datetime

import logging
logger=logging.getLogger(__name__)
del(logging)

from tornado import websocket

from .protocol import Protocol


class Client(Protocol):

    KEEPALIVE_TIMEOUT = 2 # seconds
    keepalive=None

    FUNC_MESSAGE_FROM_SERVER='message_from_server'
    
    funcs=[
        Protocol.OK,
        Protocol.ERROR,
        Protocol.EXC,
        FUNC_MESSAGE_FROM_SERVER,
        ]

    ws_connection=None # available after successfull connect()

    def __init__(self, args, ioloop=None):
        Protocol.__init__(self, args, ioloop)

    def connect(self):
        #logger.info('connect %s' % self.args)
        self.ws=websocket.websocket_connect(self.args.url)
        self.ws.add_done_callback(self.ws_connection_cb)
        return self.ws

    def ws_connection_cb(self, conn):
        self.ws_connection=conn.result()
        self.ws_connection.on_message=self.on_message # Overwrite method. Dirty, but AFAIK inheritance is not possible here.
        self.keepalive = self.ioloop.add_timeout(datetime.timedelta(seconds=self.KEEPALIVE_TIMEOUT), self.do_keep_alive)

    def do_keep_alive(self, *args, **kwargs):
        logger.info('---> do_keep_alive')
        stream = self.ws_connection.protocol.stream
        if not stream.closed():
            self.keepalive = stream.io_loop.add_timeout(datetime.timedelta(seconds=self.KEEPALIVE_TIMEOUT), self.do_keep_alive)
            self.ws_connection.protocol.write_ping("")
        else:
            self.keepalive = None

    def close(self):
        logger.info('---> close')
        if self.keepalive is not None:
            keepalive = self.keepalive
            self.keepalive = None
            self.ioloop.remove_timeout(keepalive)
        self.connect()

    def run_forever(self):
        self.ioloop.start()

    def stop(self):
        self.ioloop.stop()

    def message_from_server(self, request):
        if self.args.exit_after_message_from_server:
            logger.info('exit_after_message_from_server %s' % request)
            self.ioloop.add_timeout(3, self.stop)
            return
        
    @classmethod
    def get_argument_parser(cls):
        parser=argparse.ArgumentParser()
        parser.add_argument('--url', default='ws://localhost:8888/')
        return parser
    
    @classmethod
    def parse_args_and_run(cls):
        parser=cls.get_argument_parser()
        args=parser.parse_args()
        try:
            client = cls(args)
            client.connect()
            client.run_forever()
        except KeyboardInterrupt:
            client.close()

