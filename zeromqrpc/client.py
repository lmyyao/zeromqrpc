# encoding=utf8
import functools

import msgpack
import zmq


class Client(object):
    def __init__(self):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)

    def connect(self, host, port):
        self._socket.connect("tcp://{0}:{1}".format(host, port))

    def __getattr__(self, item):
        return functools.partial(self._send, item)

    def _send(self, name, *args, **kwargs):
        msg = msgpack.packb({"name": name, "args": args, "kwargs": kwargs})
        self._socket.send(msg)
        return msgpack.unpackb(self._socket.recv(), encoding="utf8")



