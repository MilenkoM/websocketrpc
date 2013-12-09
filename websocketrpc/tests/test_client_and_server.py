import os
import tempfile
import unittest
import subprocess
import pkg_resources

import logging
logger=logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.websocket import websocket_connect

import websocketrpc.tests.client
from websocketrpc.tests import OK

class TestRpcClient(websocketrpc.tests.client.TestClient):
    def __init__(self, ioloop, test_case):
        websocketrpc.tests.client.TestClient.__init__(self, ioloop=ioloop)
        self.test_case=test_case

    def ok(self):
        return self.test_case.stop(OK)

    def ws_connection_cb(self, conn):
        # Called after the websocket to the server is connected.
        websocketrpc.Client.ws_connection_cb(self, conn)

class TestRpc(AsyncHTTPTestCase):
    def get_app(self):
        from websocketrpc.tests import server
        return server.Application()

    @gen_test
    def test_websocket_callbacks(self):
        # See websocket_test.py (tornado) test_websocket_callbacks()
        websocket_connect(
            'ws://localhost:%d/jsonrpc' % self.get_http_port(),
            io_loop=self.io_loop, callback=self.stop)
        client=TestRpcClient(self.io_loop, self)
        client.ws_connection_cb(self.wait())

        client.call('foo', on_reply=client.on_fail_reply, on_error=client.on_good_error)
        self.assertEqual(OK, self.wait())

        client.call('reverse', args=['abcd'], on_reply=client.on_reverse_reply, on_error=client.on_fail_error)
        self.assertEqual(OK, self.wait())

        client.call('test_datatypes', on_reply=client.on_test_datatypes_reply, on_error=client.on_fail_error)
        self.assertEqual(OK, self.wait())
