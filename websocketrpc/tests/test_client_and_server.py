import os
import tempfile
import unittest
import subprocess
import pkg_resources

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.websocket import websocket_connect
import tornado.web

import websocketrpc
from websocketrpc.server import Procedure
from websocketrpc.tests import OK, test_datatypes

class TestRpcClient(websocketrpc.Client):

    def __init__(self, ioloop, test_case):
        websocketrpc.Client.__init__(self, ioloop=ioloop)
        self.test_case = test_case
        self.reply_n_times_seen = set()

    def ok(self):
        return self.test_case.stop(OK)

    def on_reply_n_times(self, i):
        self.reply_n_times_seen.add(i)
        if self.reply_n_times_seen == set([
                None,  # This is from the first call. 3 calls follow later.
                0, 1, 2]):
            self.test_case.stop(OK)
            
    def on_exception_good(self, message):
        self.test_case.assertEqual('''ValueError('foo',)''', message.error)
        return self.test_case.stop(OK)

    def on_reverse_reply(self, mystring):
        assert mystring == 'dcba', mystring
        logger.info('reverse OK')
        self.ok()

    def on_fail_reply(self, data):
        raise Exception(data)

    def on_error_good(self, error_response):
        assert error_response.error == "Method 'foo' not implemented", error_response.error
        logger.info(
            'error_response ... good, that is what I wanted: %s' %
            error_response.serialize())
        self.ok()

    def on_error_fail(self, error_response):
        raise Exception(error_response.serialize())

    def on_test_datatypes_reply(self, result):
        assert result == test_datatypes
        logging.info('test_datatypes: OK')
        self.ok()

def do_reverse(mystring):
    return ''.join(reversed(mystring))


def do_test_datatypes():
    return test_datatypes

def raise_exception():
    raise ValueError('foo')

class TestRpcHandler(websocketrpc.server.RPCSocketHandler):
    procedures = {
        'reverse': Procedure(do_reverse),
        'test_datatypes': Procedure(do_test_datatypes),
        'raise_exception': Procedure(raise_exception),
    }

    def __init__(self, *args, **kwargs):
        websocketrpc.server.RPCSocketHandler.__init__(self, *args, **kwargs)
        self.procedures = dict(self.procedures)  # class level to object level
        self.procedures.update({
            'reply_n_times': self.reply_n_times,
        })

    def reply_n_times(self, json_request):
        n_times = json_request.args[0]

        def reply(i):
            self.return_result(i, json_request)

        for i in range(n_times):
            self.stream.io_loop.add_callback(reply, i)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/jsonrpc", TestRpcHandler),
        ]
        tornado.web.Application.__init__(self, handlers)



class TestRpc(AsyncHTTPTestCase):

    def get_app(self):
        return Application()

    @gen_test
    def test_websocket_callbacks(self):
        # See websocket_test.py (tornado) test_websocket_callbacks()
        websocket_connect(
            'ws://localhost:%d/jsonrpc' % self.get_http_port(),
            io_loop=self.io_loop, callback=self.stop)
        client = TestRpcClient(self.io_loop, self)
        client.ws_connection_cb(self.wait())

        client.call(
            'foo',
            on_reply=client.on_fail_reply,
            on_error=client.on_error_good)
        self.assertEqual(OK, self.wait())

        client.call(
            'reverse',
            args=['abcd'],
            on_reply=client.on_reverse_reply,
            on_error=client.on_error_fail)
        self.assertEqual(OK, self.wait())

        client.call(
            'test_datatypes',
            on_reply=client.on_test_datatypes_reply,
            on_error=client.on_error_fail)
        self.assertEqual(OK, self.wait())

        client.call(
            'reply_n_times',
            args=[3],
            on_reply=client.on_reply_n_times,
            on_error=client.on_error_fail)
        self.assertEqual(OK, self.wait())

        client.call(
            'raise_exception',
            on_reply=client.on_fail_reply,
            on_error=client.on_exception_good)
        self.assertEqual(OK, self.wait())
