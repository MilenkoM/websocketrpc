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

class TestRpc(AsyncHTTPTestCase):
    def get_app(self):
        from websocketrpc.tests import server
        return server.Application()

    @gen_test
    def test_websocket_callbacks(self):
        websocket_connect(
            'ws://localhost:%d/jsonrpc' % self.get_http_port(),
            io_loop=self.io_loop, callback=self.stop)
        ws = self.wait().result()
        client=websocketrpc.tests.client.TestClient(ioloop=self.io_loop)
        logger.info('foo')
        assert 0, self.wait()
        ws.write_message('hello')
        ws.read_message(self.stop)
        response = self.wait().result()
        self.assertEqual(response, 'hello')
        ws.close()
        yield self.close_future
