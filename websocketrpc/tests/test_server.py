import unittest
import argparse
import subprocess

TEST_SERVER_PORT=18937
from websocketrpc import Server, websocket

class MyTestCase(unittest.TestCase):
    def test_start(self):
        cmd=['python', __file__, '--port=%s' % TEST_SERVER_PORT]
        pipe=subprocess.Popen(cmd)
        try:
            self._test_start(pipe)
        finally:
            pipe.terminate()

    def _test_start(self, pipe):
        pass

class TestServer(Server, websocket.WebSocketHandler): # TODO switch from multiple inheritance to delegation

    def __init__(self, *args, **kwargs):
        # gets called on first request.
        Server.__init__(self, **kwargs)
        websocket.WebSocketHandler.__init__(self, *args)

def main():
    TestServer.parse_args_and_run()

if __name__=='__main__':
    main()
