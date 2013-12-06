import json

CLS_REQUEST='request'
CLS_REPLY_OK='reply-ok'
CLS_REPLY_EXC='reply-exc'

classes=[
    CLS_REQUEST,
    CLS_REPLY_OK,
    CLS_REPLY_EXC,
    ]

class BaseRequest(object):
    reply=False

    def __init__(self, cls, func_str, call_id, data, ws_connection):
        assert cls in classes
        self.cls=cls
        self.func_str=func_str
        self.call_id=call_id
        self.data=data
        self.ws_connection=ws_connection
        
    def __str__(self):
        return '<%s %s %s %s %s>' % (self.__class__.__name__, self.cls, self.func_str, self.call_id, self.data)

    def __repr__(self):
        return str(self)
    
    def finish(self, protocol, result):
        raise NotImplementedError()

    def serialize(self):
        return json.dumps([self.func_str, self.cls, self.call_id, self.data])

class ClientRequest(BaseRequest):
    'Request class for the client part'
    def __init__(self, func_str, call_id, data, ws_connection, on_reply, on_exception):
        BaseRequest.__init__(self, CLS_REQUEST, func_str, call_id, data, ws_connection)
        self.on_reply=on_reply
        self.on_exception=on_exception

    def finish(self, protocol, result):
        return protocol.send_ok(self, result)

class ServerRequest(BaseRequest):
    def __init__(self, func_str, call_id, data, ws_connection):
        BaseRequest.__init__(self, CLS_REQUEST, func_str, call_id, data, ws_connection)
    
class ServerReply(BaseRequest):
    reply=True

    def __init__(self, func_str, call_id, data, ws_connection):
        BaseRequest.__init__(self, CLS_REPLY_OK, func_str, call_id, data, ws_connection)

    def finish(self, protocol, result):
        protocol.handle_reply(self, result)

class ServerReplyExc(ServerReply):
    def __init__(self, request, message):
        BaseRequest.__init__(self, CLS_REPLY_EXC, request.func_str, request.call_id, message, request.ws_connection)
