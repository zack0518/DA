import socket
from threading import Thread

class ServerThread(Thread):
    threads = {}
    outThreads = {}
    def __init__(self, ip, port):
        Thread.__init__(self)
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpServer.bind((SERVER_IP, SERVER_PORT))

    def run(self):
        print('[+] New server thread start')
        '''
        for _ in outList:
            oThread = OutThread()
            oThread.start()
            self.outThreads[(ip,port)] = oThread
            print(self.outThreads.keys())
        '''
        while True:
            self.tcpServer.listen()
            #print('Server: wait for new connection...')
            (conn, (ip,port)) = self.tcpServer.accept()
            cThread = ClientThread(ip, port, conn, self)
            cThread.start()
            self.threads[(ip,port)] = cThread
            print(self.threads.keys())

    def removeCThreads(self, ip, port):
        d = dict(self.threads)
        del d[(ip,port)]
        self.threads = d

    def removeOThreads(self, ip, port):
        d = dict(self.outThreads)
        del d[(ip,port)]
        self.outThreads = d


class ClientThread(Thread):
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
        self.server.removeCThreads(self.ip,self.port)
        print('Connection closed - {}:{}'.format(self.ip,self.port))


class OutThread(Thread):
    def __init__(self, host, port, sock=None):
        Thread.__init__(self)
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.host = host
        self.port = port

    def run(self):
        self.sock.connect((self.host, self.port))
        print('Connection request -> {}:{}'.format(self.host, self.port))
        i = 0
        while True:
            try:
                msg = 'Req: ' + str(i)
                self.sock.sendall(msg.encode())
                res = self.sock.recv(8192)
                if not res:
                    break
                print(res.decode())
            except:
                print('Connection Error - {}:{}'.format(self.host,self.port))
                break
        self.sock.close()
        self.server.removeOThreads(self.host,self.port)
        print('Connection closed - {}:{}'.format(self.ip,self.port))


if __name__ == '__main__':
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 20000

    s = ServerThread(SERVER_IP, SERVER_PORT)
    s.start()
