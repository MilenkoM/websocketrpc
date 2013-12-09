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

import websocketrpc.tests.client
from websocketrpc.tests import OK
import websocketrpc.tests.server


class TestRpcClient(websocketrpc.tests.client.TestClient):

    def __init__(self, ioloop, test_case):
        websocketrpc.tests.client.TestClient.__init__(self, ioloop=ioloop)
        self.test_case = test_case
        self.reply_n_times_seen = set()

    def ok(self):
        return self.test_case.stop(OK)

    def ws_connection_cb(self, conn):
        # Called after the websocket to the server is connected.
        websocketrpc.Client.ws_connection_cb(self, conn)

    def on_reply_n_times(self, i):
        self.reply_n_times_seen.add(i)
        if self.reply_n_times_seen == set([
                None,  # This is from the first call. 3 calls follow later.
                0, 1, 2]):
            self.test_case.stop(OK)
            
    def on_exception_good(self, message):
        self.test_case.assertEqual('''ValueError('foo',)''', message.error)
        return self.test_case.stop(OK)

class TestRpcHandler(websocketrpc.tests.server.TestHandler):

    def __init__(self, *args, **kwargs):
        websocketrpc.tests.server.TestHandler.__init__(self, *args, **kwargs)
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
        from websocketrpc.tests import server
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
