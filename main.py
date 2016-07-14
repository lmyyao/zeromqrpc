# encoding=utf8

from zeromqrpc.server import Task, Server, Application


class RPCTask(Task):
    def hello(self, world):
        return world

    def sum(self, x, y):
        return x + y


class App(Application):
    def set_response(self, msg):
        return {"OK": msg}

    def do_error(self, e, code=500):
        return {"error": str(e.args[0]), "code": code}


if __name__ == '__main__':


    server = Server("127.0.0.1", "5560", App(RPCTask()))
    server.start()


