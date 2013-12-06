from websocketrpc import Client

class TestClient(Client):
    def on_reply(self, data):
        assert 0, data

    def ws_connection_cb(self, conn):
        Client.ws_connection_cb(self, conn)
        ### start call
        self.call('foo', on_reply=self.on_reply)

def main():
    TestClient.parse_args_and_run()

if __name__=='__main__':
    main()
