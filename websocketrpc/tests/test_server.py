#!/usr/bin/env python
# based on tornado chat example

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options
from websocketrpc.server import RPCSocketHandler

define("port", default=8888, help="run on the given port", type=int) # TODO ???

def do_reverse(mystring):
    return mystring.reverse()

class TestHandler(RPCSocketHandler):
    procedures={
        'reverse': do_reverse,
        }
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/jsonrpc", TestHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
