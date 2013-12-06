import os
import tempfile
import unittest
import subprocess
import pkg_resources

class TestRPC(unittest.TestCase):
    def test_client_and_server(self):
        server=pkg_resources.resource_filename('websocketrpc', 'tests/websocketrpc_server.py')
        assert os.path.exists(server), server
        client=pkg_resources.resource_filename('websocketrpc', 'tests/websocketrpc_client.py')
        assert os.path.exists(client), client
        with tempfile.TemporaryFile() as fd:
            server_pipe=subprocess.Popen(['python', server], stdout=fd, stderr=subprocess.STDOUT)
            client_pipe=subprocess.Popen(['python', client], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in client_pipe.stdout:
                print line

