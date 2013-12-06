# http://www.tornadoweb.org/en/stable/websocket.html#tornado.websocket.WebSocketClientConnection
# Example of websocket_connect https://gist.github.com/fcicq/5328876
import argparse
import datetime
import uuid

import logging
logger=logging.getLogger(__name__)
del(logging)

from tornado import websocket
from tornado.ioloop import IOLoop
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol, JSONRPCErrorResponse, JSONRPCSuccessResponse

class ClientProtocol(JSONRPCProtocol):
    def _get_unique_id(self):
        return unicode(uuid.uuid1())
        
class ClientRequest(object):
    'Request class for the client part'
    def __init__(self, json_request, ws_connection, on_reply, on_error):
        self.json_request=json_request # from tinyrpc
        self.ws_connection=ws_connection
        if on_reply:
            self.on_reply=on_reply
        if on_error:
            self.on_error=on_error

    def on_reply(self, result):
        '''
        This method gets overridden by the "on_reply" callback you pass to call()
        '''
        logger.info(result)

    def on_error(self, error_response):
        '''
        This method gets overridden by the "on_error" callback you pass to call()
        '''
        logger.error(error_response.serialize())

    def serialize(self):
        return self.json_request.serialize()

    @property
    def unique_id(self):
        return self.json_request.unique_id

class Client(object):

    ws_connection=None # available after successfull connect()
    
    KEEPALIVE_TIMEOUT=20

    def __init__(self, args=None, ioloop=None):
        self.wait_for_reply=dict()
        self.args=args
        if ioloop is None:
            ioloop=IOLoop.instance() # Singleton
        self.ioloop=ioloop
        self.protocol=ClientProtocol()
        self.keepalive=None

    def connect(self):
        #logger.info('connect %s' % self.args)
        self.ws=websocket.websocket_connect(self.args.url)
        self.ws.add_done_callback(self.ws_connection_cb)
        return self.ws

    def ws_connection_cb(self, conn):
        self.ws_connection=conn.result()
        self.ws_connection.on_message=self.on_message # Overwrite method. Dirty, but AFAIK inheritance is not possible here.
        self.keepalive = self.ioloop.add_timeout(datetime.timedelta(seconds=self.KEEPALIVE_TIMEOUT), self.do_keep_alive)

    def call(self, func_str, args=None, kwargs=None, on_reply=None, on_error=None):
        '''
         Caller calls func on remote
         Example myclient.call_func(Server.FUNC_FOO, self.ws_connection, mydata) # TODO: make self.ws_connection optional.
         '''
        json_request=self.protocol.create_request(func_str, args=args, kwargs=kwargs)
        request=ClientRequest(json_request, self.ws_connection, on_reply, on_error)
        logger.info('call_func %s connection=%s' % (request, self.ws_connection))
        request.ws_connection.write_message(request.serialize())
        self.wait_for_reply[request.unique_id]=request

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

    @classmethod
    def get_argument_parser(cls):
        parser=argparse.ArgumentParser()
        parser.add_argument('--url', default='ws://localhost:8888/jsonrpc')
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

    def on_message(self, message):
        try:
            self._on_message(message)
        except Exception, exc:
            # tornado hides exceptions. We do our own logging
            logger.error(exc, exc_info=True)
            raise

    def _on_message(self, message):
        'Client: message is a reponse'
        #print 'on_message client ........... %r' % message
        if message is None:
            # happens on close: TODO: needed?
            return
        json_reply=self.protocol.parse_reply(message)
        request=self.wait_for_reply[json_reply.unique_id]
        if isinstance(json_reply, JSONRPCErrorResponse):
            request.on_error(json_reply)
            return
        elif isinstance(json_reply, JSONRPCSuccessResponse):
            request.on_reply(json_reply.result)
            return
        raise ValueError('unsupported reply: %r' % json_reply)
