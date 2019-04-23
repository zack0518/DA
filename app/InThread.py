import sys, socket, time, json
from threading import Thread


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
                self.server.process(inData.decode(), self)
                print('Received: ', inData.decode())
                #self.send(inData)
            except:
                print('Connection Error - {}:{}'.format(self.ip,self.port))
                break
        self.sock.close()
        self.server.removeIThreads(self.ip,self.port)
        print('Connection closed - {}:{}'.format(self.ip,self.port))

    def send(self, msg):
        self.sock.sendall(msg)
