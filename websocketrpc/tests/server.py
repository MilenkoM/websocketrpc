#!/usr/bin/env python
# based on tornado chat example

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path

from tornado.options import define, options
from websocketrpc.server import RPCSocketHandler, Procedure
from websocketrpc.tests import test_datatypes

define("port", default=8888, help="run on the given port", type=int)

def do_reverse(mystring):
    return ''.join(reversed(mystring))

def do_test_datatypes():
    return test_datatypes

class TestHandler(RPCSocketHandler):
    procedures={
        'reverse': Procedure(do_reverse),
        'test_datatypes': Procedure(do_test_datatypes),
        }

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/jsonrpc", TestHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
