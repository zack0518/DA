import sys, socket, time, json
from threading import Thread
from InThread import InThread
from OutThread import OutThread

# Server Thread
# Start a new server by running a server thread
class ServerThread(Thread):
    inThreads = {}  # Incoming socket threads {(ip,local_port): iThread}
    idRecord = {}   # Thread ID records {(ip,local_port): thread_listening_port}
    outThreads = {} # Outgoing socket threads {(ip,target_port): oThread}
    isCo = False    # isCoordinator flag (default: False)
    coPort = -1     # Coordinator port (default: -1)

    def __init__(self, ip, port, outList=[]):
        Thread.__init__(self)
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpServer.bind((ip, port))
        self.ip = ip
        self.port = port
        self.outList = outList
        if len(outList) == 0: # if outList is empty, set to be coordinator
            self.isCo = True

    def run(self):
        print('[+] New server thread start')

        # Create outgoing connections to existing servers
        for ip, port in self.outList:
            oThread = OutThread(ip, port, self)
            oThread.start()
            self.outThreads[(ip,port)] = oThread
            print(self.outThreads.keys())

        # Create listener to accept incoming connections
        while True:
            self.tcpServer.listen()
            (conn, (ip,port)) = self.tcpServer.accept()
            iThread = InThread(ip, port, conn, self)
            iThread.start()
            self.inThreads[(ip,port)] = iThread
            print(self.inThreads.keys())

    # Remove an incoming connection from inThreads dict
    def removeIThreads(self, ip, port):
        d = dict(self.inThreads)
        del d[(ip,port)]
        self.inThreads = d

    # Remove an outgoing connection from outThreads dict
    def removeOThreads(self, ip, port):
        d = dict(self.outThreads)
        del d[(ip,port)]
        self.outThreads = d

    def process(self, jsonMsg, ioThread):
        msg = json.loads(jsonMsg)
        ip = ioThread.ip
        port = ioThread.port
        cmd = msg['cmd']
        if cmd == 'set_id':
            self.idRecord[(ip,port)] = msg['id']
            if self.isCo:
                resMsg = {}
                resMsg['cmd'] = 'set_co'
                resMsg['co_port'] = self.port
                ioThread.send(json.dumps(resMsg).encode())
        elif cmd == 'set_co':
            print(type(msg['co_port']))
            self.coPort = msg['co_port']
        #elif cmd == 'req_token':

        #elif cmd == 'rel_token:'



if __name__ == '__main__':
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 20000

    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            SERVER_PORT = int(sys.argv[1])

    outList = []
    if SERVER_PORT > 20000:
        for i in range(SERVER_PORT-20000):
            outList.append((SERVER_IP, 20000+i))

    if len(outList) > 0:
        s = ServerThread(SERVER_IP, SERVER_PORT, outList)
    else:
        s = ServerThread(SERVER_IP, SERVER_PORT)
    s.start()
