import sys
import logging
from websocketrpc import Client

class TestClient(Client):
    def on_reply(self, data):
        assert 0, data

    def on_error(self, error_response):
        assert error_response.error=="Method foo not implemented", error_response.error
        logger.info('error_response ... good, that is what I wanted: %s' % error_response.serialize())

    def ws_connection_cb(self, conn):
        Client.ws_connection_cb(self, conn)
        ### start call
        self.call('foo', on_reply=self.on_reply, on_error=self.on_error)

def main():
    TestClient.parse_args_and_run()

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger=logging.getLogger(sys.argv[0])
    main()
else:
    logger=logging.getLogger(__name__)
    
