from zeromqrpc.client import Client

if __name__ == '__main__':
    c = Client()
    c.connect("127.0.0.1", "5559")
    mes = c.hello("world")
    print(mes)
    mes = c.hello("nihaoa")
    print(mes)
    print(c.sum(4, 5))
