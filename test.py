import zmq
import msgpack
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5559")

for request in range(1, 10):
    socket.send(b"Hello")
    message = socket.recv()
    print(msgpack.unpackb(message, encoding="utf8"))
