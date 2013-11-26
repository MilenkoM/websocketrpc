import json

class BaseRequest(object):
    reply=False

    def __init__(self, func_str, call_id, data, ws_connection):
        self.func_str=func_str
        self.call_id=call_id
        self.data=data
        self.ws_connection=ws_connection

    def __str__(self):
        return '<%s %s %s %s>' % (self.__class__.__name__, self.func_str, self.call_id, self.data)

    def __repr__(self):
        return str(self)
    
    def finish(self, protocol, result):
        raise NotImplementedError()

    def serialize(self):
        return json.dumps([self.func_str, self.call_id, self.data])

class Request(BaseRequest):
    def finish(self, protocol, result):
        return protocol.send_ok(self, result)

class Reply(BaseRequest):
    reply=True

    def finish(self, protocol, result):
        protocol.handle_reply(self, result)

