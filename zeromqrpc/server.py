# encoding=utf8
import threading
import time
import types

import msgpack
import zmq


class ZMQError(Exception):
    pass


class Server(threading.Thread):
    def __init__(self, host, port, application, pool=4):
        threading.Thread.__init__(self)
        self.context = zmq.Context()
        self.pool = range(pool)
        self.workers = []
        self.application = application
        self.host = host
        self.port = port

    def run(self):

        for _ in self.pool:
            w = Worker(self.host, self.port, self.context, self.application)
            w.start()
            self.workers.append(w)

    # doesn't work
    def join(self, timeout=None):
        for i in self.workers:
            i.join()

    # doesn't work
    def stop(self):
        for i in self.workers:
            i.stop()
        self.context.term()


class Worker(threading.Thread):
    def __init__(self, host, port, context, application):
        threading.Thread.__init__(self)
        self.context = context
        self.app = application
        self.host = host
        self.port = port
        self._stop = threading.Event()
        self._stop.set()

    def run(self):
        worker = self.context.socket(zmq.REP)
        worker.connect('tcp://{0}:{1}'.format(self.host, self.port))
        while self._stop.isSet():
            time.sleep(1)
            msg = worker.recv()
            message = self.app.do(msg)
            worker.send(msgpack.packb(message))
        worker.close()

    def stop(self):
        self._stop.clear()


class Task(object):
    def __new__(cls, *args, **kwargs):
        router = {}
        bases = list(cls.__bases__)
        bases.append(cls)
        for base in bases:
            for key, value in base.__dict__.items():
                if isinstance(value, types.FunctionType):
                    router[key] = value
        cls.router = router
        return object.__new__(cls, *args, **kwargs)


class Application(object):
    def __init__(self, task):
        self.task = task

    def do(self, msg):
        try:
            name, args, kwargs = self.parse(msg)
            if name in self.task.router:
                output = self.task.router.get(name)(self.task, *args, **kwargs)
                return self.set_response(output)
            raise ZMQError("No function: {}".format(name), 2)
        except (TypeError, ZMQError)as e:
            if hasattr(self, "do_error") and isinstance(self.do_error, types.MethodType):
                if isinstance(e, TypeError):
                    return self.do_error(e, 3)
                else:
                    return self.do_error(e, e.args[-1])
            else:
                return {"error": "Server Error", "code": 500}

    def set_response(self, msg):
        return msg

    def parse(self, msg):
        try:
            message = msgpack.unpackb(msg, encoding="utf8")
            return message["name"], message["args"], message["kwargs"]
        except Exception:
            raise ZMQError("Send Message Error", 1)
