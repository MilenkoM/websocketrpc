import uuid
import json

import logging
logger=logging.getLogger(__name__)
del(logging)

from tornado.ioloop import IOLoop

from websocketrpc.messages import Request, Reply

class ProtocolException(Exception):
    pass

class Protocol(object):
    '''
    Maybe it would have been better to use an existing protocol like http://wamp.ws/
    But up to now there seems to be no WAMP server for tornado.
    '''
    
    OK='ok'
    ERROR='error'
    EXC='exc'
    MESSAGE='message'
    REPLIES=[OK, ERROR]

    OtherEndPoint=None # class of other end point

    def call_func(self, func_str, ws_connection, data=None):
        '''
         Caller calls func on remote
         Example myclient.call_func(Server.FUNC_FOO, self.ws_connection, mydata) # TODO: make self.ws_connection optional.
         '''
        if not func_str in self.OtherEndPoint.funcs:
            raise ProtocolException('Func %r unknown. Known: %s' % (
                    func_str, self.OtherEndPoint.funcs))
        call_id=unicode(uuid.uuid1())
        request=Request(func_str, call_id, data, ws_connection)
        logger.info('call_func %s connection=%s' % (request, ws_connection))
        request.ws_connection.write_message(request.serialize())
        self.wait_for_reply[call_id]=request

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
        
    def send_protcol_error(self, message):
        request=Request(func_str='error', call_id='error', data=None)
        self.send_error(request, message)

    def send_error(self, request, message):
        self.send_reply(Protocol.ERROR, request, {Protocol.MESSAGE: message})

    def send_exc(self, request, message):
        self.send_reply(Protocol.EXC, request, {Protocol.MESSAGE: message})
    
    def send_ok(self, request, result):
        self.send_reply(Protocol.OK, request, result)
        
    def send_reply(self, return_code, request, result):
        request.ws_connection.write_message(json.dumps([return_code, request.call_id, result])) # TODO: only one json.dumps() in code.

    def handle_reply(self, reply, result):
        'Caller gets a reply'
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

    def on_message(self, message):
        u'''
        WebSocket API: message is a string.
        We build the Protocol API on top of this method.
        '''
        if message is None:
            # happens on close: TODO: needed?
            return
        try:
            func_str, call_id, data = json.loads(message)
        except ValueError, exc:
            msg='Protocol Error: %s' % exc
            logger.warn(msg)
            return self.send_protocol_error(msg)

        if func_str in Protocol.REPLIES:
            request=Reply(func_str, call_id, data, self.ws_connection)
        else:
            request=Request(func_str, call_id, data, self.ws_connection)

        logger.info('received %r' % request)
            
        if not request.func_str in self.funcs:
            return self.send_error(request, 'Unknown Method %r %s' % (request.func_str, request))

        func=getattr(self, request.func_str, None)
        if func is None:
            logger.warn('%s unknown' % request.func_str)
            return
        try:
            result=func(request)
        except Exception, exc:
            return self.send_exc(request, unicode(exc))
        request.finish(self, result)

