from server import Server
from client import Client

Client.OtherEndPoint=Server
Server.OtherEndPoint=Client

from tornado import websocket
from tornado.ioloop import IOLoop
from tornado.web import Application
