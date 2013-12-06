import uuid
import json

import logging
logger=logging.getLogger(__name__)
del(logging)

from tornado.ioloop import IOLoop

class ProtocolException(Exception):
    pass

class Protocol(object):
    
    def __init__(self, args, ioloop=None):
        self.wait_for_reply=dict()
        self.args=args
        if ioloop is None:
            ioloop=IOLoop.instance() # Singleton
        self.ioloop=ioloop

    def ok(self, request):
        pass

    def error(self, request):
        logger.warn(request)
        
    def exc(self, request):
        logger.error('Exc: %s' % request)
        
    def handle_reply(self, reply, result):
        'Caller gets a reply'
        assert 0, '???'
        assert reply.reply, reply
        old_request=self.wait_for_reply.pop(reply.call_id, None)
        if old_request is None:
            logger.warn('Received Reply, but no wait_for_reply entry: %s' % reply)
            return
        msg='Reply: %s' % reply

        if reply.func_str==Protocol.EXC:
            print '################'
            assert 0
        if reply.func_str!=Protocol.OK:
            logger.warn(msg)
            return

        logger.info(msg)
        reply_func_str='reply_%s' % old_request.func_str
        method=getattr(self, reply_func_str, None)
        if method:
            return method(old_request, reply)
        logger.warn('No callback %r' % reply_func_str)

    def deserialize(self, data):
        return json.loads(data)

