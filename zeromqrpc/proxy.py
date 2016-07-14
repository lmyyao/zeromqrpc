# encoding=utf8
import zmq


def get_event_loop(front, back):
    loop = PollLoop()
    loop.bind(front, back)
    return loop


class PollLoop(object):
    def __init__(self):
        self.context = zmq.Context()
        self.frontend = self.context.socket(zmq.XREP)
        self.backend = self.context.socket(zmq.XREQ)
        self.poller = zmq.Poller()

    def run(self):

        self.poller.register(self.frontend, zmq.POLLIN)
        self.poller.register(self.backend, zmq.POLLIN)
        while True:
            socks = dict(self.poller.poll())

            if socks.get(self.frontend) == zmq.POLLIN:
                message = self.frontend.recv()
                more = self.frontend.getsockopt(zmq.RCVMORE)
                if more:
                    self.backend.send(message, zmq.SNDMORE)
                else:
                    self.backend.send(message)

            if socks.get(self.backend) == zmq.POLLIN:
                message = self.backend.recv()
                more = self.backend.getsockopt(zmq.RCVMORE)
                if more:
                    self.frontend.send(message, zmq.SNDMORE)
                else:
                    self.frontend.send(message)
        self.frontend.close()
        self.backend.close()
        self.context.term()

    def bind(self, front, back):
        format_style = "tcp://{}:{}".format
        self.frontend.bind(format_style(*front))
        self.backend.bind(format_style(*back))


if __name__ == '__main__':
    loop = get_event_loop(("127.0.0.1", "5559"), ("127.0.0.1", "5560"))
    loop.run()
