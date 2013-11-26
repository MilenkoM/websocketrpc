from websocketrpc import Client
from websocketrpc.tests.test_server import TestServer

class TestClient(Client):
    def ws_connection_cb(self, conn):
        Client.ws_connection_cb(self, conn)
        self.call_func(TestServer.FUNC_TEST_EXCEPTION, self.ws_connection)

def main():
    TestClient.parse_args_and_run()

if __name__=='__main__':
    main()
