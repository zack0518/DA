import sys, socket, time
from threading import Thread

class ServerThread(Thread):
    inThreads = {}
    outThreads = {}
    def __init__(self, ip, port, outList=[]):
        Thread.__init__(self)
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpServer.bind((SERVER_IP, SERVER_PORT))
        self.outList = outList

    def run(self):
        print('[+] New server thread start')

        for ip, port in self.outList:
            oThread = OutThread(ip, port, self)
            oThread.start()
            self.outThreads[(ip,port)] = oThread
            print(self.outThreads.keys())

        while True:
            self.tcpServer.listen()
            #print('Server: wait for new connection...')
            (conn, (ip,port)) = self.tcpServer.accept()
            iThread = InThread(ip, port, conn, self)
            iThread.start()
            self.inThreads[(ip,port)] = iThread
            print(self.inThreads.keys())

    def removeIThreads(self, ip, port):
        d = dict(self.inThreads)
        del d[(ip,port)]
        self.inThreads = d

    def removeOThreads(self, ip, port):
        d = dict(self.outThreads)
        del d[(ip,port)]
        self.outThreads = d


class InThread(Thread):
    def __init__(self, ip, port, sock, server):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.server = server
        print('[+] New client thread start')
        print('Got connection from {}:{}'.format(ip,port))

    def run(self):
        while True:
            try:
                inData = self.sock.recv(8192)
                if not inData:
                    break
                print('Received: ', inData.decode())
                self.sock.sendall(inData)
            except:
                print('Connection Error - {}:{}'.format(self.ip,self.port))
                break
        self.sock.close()
        self.server.removeIThreads(self.ip,self.port)
        print('Connection closed - {}:{}'.format(self.ip,self.port))


class OutThread(Thread):
    def __init__(self, host, port, server, sock=None):
        Thread.__init__(self)
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.host = host
        self.port = port
        self.server = server

    def run(self):
        try:
            self.sock.connect((self.host, self.port))
        except:
            print('Could not connect to {}.{}'.format(self.host, self.port))
            thread.exit()
        print('Connection request -> {}:{}'.format(self.host,self.port))
        i = 0
        while True:
            try:
                msg = 'Req: ' + str(i)
                self.sock.sendall(msg.encode())
                res = self.sock.recv(8192)
                if not res:
                    break
                print(res.decode())
                i += 1
                time.sleep(2)
            except:
                print('Connection Error - {}:{}'.format(self.host,self.port))
                break
        self.sock.close()
        self.server.removeOThreads(self.host,self.port)
        print('Connection closed - {}:{}'.format(self.host,self.port))


if __name__ == '__main__':
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 20000

    if len(sys.argv) > 0:
        if sys.argv[1].isdigit():
            SERVER_PORT = int(sys.argv[1])

    outList = []
    if SERVER_PORT > 20000:
        for i in range(SERVER_PORT - 20000):
            outList.append((SERVER_IP, 20000+i))

    print(SERVER_PORT)
    print(outList)
    print(sys.argv)
    if len(outList) > 0:
        s = ServerThread(SERVER_IP, SERVER_PORT, outList)
    else:
        s = ServerThread(SERVER_IP, SERVER_PORT)
    s.start()
