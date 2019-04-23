import sys, socket, time, json
from threading import Thread


class OutThread(Thread):
    def __init__(self, ip, port, server, sock=None):
        Thread.__init__(self)
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.ip = ip
        self.port = port
        self.server = server

    def run(self):
        try:
            self.sock.connect((self.ip, self.port))
        except:
            print('Could not connect to {}:{}'.format(self.ip, self.port))
            sys.exit()
        print('Connection request -> {}:{}'.format(self.ip,self.port))

        msg = {}
        msg['cmd'] = 'set_id'
        msg['id'] = self.port
        self.send(json.dumps(msg).encode())

        while True:
            try:
                res = self.sock.recv(8192)
                if not res:
                    break
                print(res.decode())
                self.server.process(res.decode(), self)

            except:
                print('Connection Error - {}:{}'.format(self.ip,self.port))
                break
        self.sock.close()
        self.server.removeOThreads(self.ip,self.port)
        print('Connection closed - {}:{}'.format(self.ip,self.port))

    def send(self, msg):
        self.sock.sendall(msg)
