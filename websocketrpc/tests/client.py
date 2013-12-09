import sys
import logging

from websocketrpc import Client
from websocketrpc.tests import test_datatypes


class TestClient(Client):

    def ok(self):
        # Implemented in tornado TestRpc
        pass

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

    def ws_connection_cb(self, conn):
        # Called after the websocket to the server is connected.
        Client.ws_connection_cb(self, conn)
        self.call(
            'foo',
            on_reply=self.on_fail_reply,
            on_error=self.on_error_good)
        self.call(
            'reverse',
            args=['abcd'],
            on_reply=self.on_reverse_reply,
            on_error=self.on_fail_error)
        self.call(
            'test_datatypes',
            on_reply=self.on_test_datatypes_reply,
            on_error=self.on_fail_error)


def main():
    TestClient.parse_args_and_run()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(sys.argv[0])
    main()
else:
    logger = logging.getLogger(__name__)
