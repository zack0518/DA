import sys, socket, time, json, queue
from threading import Thread
from InThread import InThread
from OutThread import OutThread
from flask import Flask, request
import flask
app = Flask(__name__)
global userData
# Server Thread
# Start a new server by running a server thread
class ServerThread(Thread):
    inThreads = {}   # Incoming socket threads {(ip,local_port): iThread}
    idRecord = {}    # Thread ID records {(ip,local_port): thread_listening_port}
    outThreads = {}  # Outgoing socket threads {(ip,target_port): oThread}
    isCo = False     # isCoordinator flag (default: False)
    coPort = -1      # Coordinator port (default: -1)
    hasToken = False # hasToken flag (default: False)

    waitQueue = queue.Queue() # queue holding the server waiting for token

    def __init__(self, ip, port, outList=[]):
        Thread.__init__(self)
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpServer.bind((ip, port))
        self.ip = ip
        self.port = port
        self.outList = outList
        self.isReceived = True
        if len(outList) == 0: # if outList is empty, set to be coordinator
            self.isCo = True
            self.coPort = port
            self.hasToken = True

    def run(self):
        print('[+] New server thread start')

        # Create outgoing connections to existing servers
        for ip, port in self.outList:
            oThread = OutThread(ip, port, self)
            oThread.start()
            self.outThreads[(ip,port)] = oThread
            print("self.outThreads ",self.outThreads)
            print(self.outThreads.keys())

        # Create listener to accept incoming connections
        while True:
            self.tcpServer.listen()
            (conn, (ip,port)) = self.tcpServer.accept()
            iThread = InThread(ip, port, conn, self)
            iThread.start()
            self.inThreads[(ip,port)] = iThread
            print("self.inThreads ", self.inThreads)
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

    """
    Process the received message, main logic of bully algorithm 
    set_co - set the given port as coordinator
    set_id - the connected node port
    message at thie point will send to the original message sender
    """
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
            self.coPort = msg['co_port']

        elif cmd == 'election':
            resMsg = {}
            resMsg['cmd'] = 'disagree'
            ioThread.send(json.dumps(resMsg).encode())
            # after disagree start election
            self.election()

        elif cmd == 'victory':
            self.coPort = msg['co_port']
            print("Current coordinator is : ", self.coPort)

        elif cmd == 'req_token':
            if self.hasToken:
                self.sendToken(ioThread)

        elif cmd == 'token':
            print("token recieved")
            self.hasToken = True

        elif cmd == 'rel_token:':
            if self.isCo and self.waitQueue.qsize != 0:
                t = self.waitQueue.get()
                self.sendToken(t)
            else:
                self.hasToken = True
    """
    election section 
    If there is no connections, elect itself as the coordiantor
    If P has the highest process id, it sends a Victory message to all other processes and becomes the new Coordinator. 
    Otherwise, P broadcasts an Election message to all other processes with higher process IDs than itself.
    """
    def election(self):
        msg = {}
        msg['cmd'] = 'election'
        # get all nodes of the server
        outList = [self.outThreads[k] for k in self.outThreads.keys() if self.outThreads[k].port]
        inList = [self.inThreads[k] for k in self.inThreads.keys() if self.inThreads[k].port]

        self.isReceived = False
        higherIDs = []
        if len(outList) == 0 and len(inList) == 0:
            self.coPort = self.port
            print("Current coordinator is : ", self.coPort)
        else:
            # first send out message to outgoing nodes with higher id
            for out in outList:
                if self.port < out.port:
                    higherIDs.append(out.port)
                    out.send(json.dumps(msg).encode())

            # then send out message to ingoing nodes with lower id
            for i in inList:
                ip_port = (i.ip, i.port)
                localPort = self.idRecord.get(ip_port)
                if self.port < localPort:
                    higherIDs.append(localPort)
                    targetThread = self.inThreads[ip_port]
                    targetThread.send(json.dumps(msg).encode())

        print("# isReceived ", self.isReceived)
        # wait a time interval for response
        time.sleep(1)
        # If higherId list is empty it means that the current P has the highest process id,
        # it sends a Victory message to all other processes and becomes the new Coordinator.
        # Or If the current P receives no Answer after sending an Election message,
        # then it broadcasts a Victory message to all other processes and becomes the Coordinator
        if len(higherIDs) == 0 or self.isReceived == False:
            self.coPort = self.port
            self.broadCastVicMsg(inList, outList)
        self.isReceived = True
        print("Current coordinator is : ", self.coPort)

    """
    broadcast a victory message
    """
    def broadCastVicMsg(self, inList, outList):
        msg = {}
        msg['cmd'] = 'victory'
        msg['co_port'] = self.port
        # boardcast vitory message
        for out in outList:
            out.send(json.dumps(msg).encode())
        for i in inList:
            i.send(json.dumps(msg).encode())

    """
    This function sends request to the coordinator 
    Then checks the time interval between the sent message and received message
    """
    def requestToCoordinator(self):

        print("request toekn to coordinator")
        resMsg = {}
        resMsg['cmd'] = 'req_token'
        # check if the coordinator is offline
        # if it is, start election
        # if not, directly send req_token message
        if self.isCoordinatorOffline() and not self.isCo:
            print("Coordinator offline, start election")
            self.election()
        # if itself is not coordinator request token
        elif not self.isCo:
            coThread = self.outThreads[(self.ip, self.coPort)]
            coThread.send(json.dumps(resMsg).encode())

    """
    Check if the cooridinator is offline after send out msg
    """
    def isCoordinatorOffline(self):
        coKey = (self.ip, self.coPort)
        if coKey in self.outThreads or coKey in self.inThreads:
            return False
        return True

    def transfer(self, toAccount, amount):
        global userAccount
        global currentUser

        self.toAccount = toAccount
        self.amount = amount
        print('Recieved from client : {}:{}'.format(self.toAccount, self.amount))
        
        #change token
        while not self.hasToken:
            print('token not received yet')
            # wait a time interval for token
            time.sleep(1)
            continue
        #change data in js db
        jsonDb = open('db.json', 'r')
        data = json.load(jsonDb)
        print(data)
        jsonDb.close()

        userB = float(data[userAccount]['balance'])
        balance = str(userB - float(amount))
        data[userAccount]['balance'] = balance
        currentUser['balance'] = balance
        toUserB = float(data[toAccount]["balance"])
        data[toAccount]["balance"] = str(toUserB + float(amount))

        jsonDb = open("db.json", "w+")
        jsonDb.write(json.dumps(data))
        jsonDb.close()

        print("transfer success")
        #release token to coordinator if not coordinator
        if not self.isCo:
            print("releas token")
            resMsg = {}
            resMsg['cmd'] = 'rel_tokem'
            coThread = self.outThreads[(self.ip, self.coPort)]
            coThread.send(json.dumps(resMsg).encode())
            self.hasToken = False

    """
    This function sends token to the server
    """
    def sendToken(self, ioThread):
        self.waitQueue.put(ioThread)
        t = self.waitQueue.get()
        resMsg = {}
        resMsg['cmd'] = 'token'
        t.send(json.dumps(resMsg).encode())
        print("Token sent to server: {}:{}".format(t.ip, t.port))

"""
HTTP Request handler section
"""
currentUser = ""
userAccount = ""
@app.route('/')
def home():
    return "Connected To Server"

@app.route('/loginInfo', methods=["POST"])
def loginQuery():
    data = request.get_data()
    data = data.decode("utf-8")
    # get the request response
    data = json.loads(data)
    q_res = {}
    res = None
    if not str(data['account']) in userData:
        res = "User not exist"
        q_res['res'] = res
        res = flask.make_response(flask.jsonify(q_res))
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Methods'] = 'POST'
        res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
        return res
    else:
        user = userData[str(data['account'])]
    global currentUser
    global userAccount
    userAccount = str(data['account'])
    currentUser= user
    if str(user['password']) == str(data['password']):
        res = "Login Success"
    else:
        res = "Password Incorrect"
    print("User login : ", res)
    q_res['res'] = res
    res = flask.make_response(flask.jsonify(q_res))
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'POST'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res

@app.route('/balanceRequest', methods=["GET"])
def balanceQuery():
    global currentUser
    q_res = {}
    balance = currentUser['balance']
    q_res['balance'] = balance
    res = flask.make_response(flask.jsonify(q_res))
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res

"""
handel transfer event , ask for token 
"""
@app.route('/transferEvent', methods=["POST"])
def transferEvent():
    data = request.get_data()
    data = data.decode("utf-8")
    # get the request response
    data = json.loads(data)
    # ask for token
    serverInstance.requestToCoordinator()
    print(data)
    serverInstance.transfer(data['account'], data['amount'])
    q_res = {}
    res = flask.make_response(flask.jsonify(q_res))
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res

if __name__ == '__main__':
    """
    load the local json file 
    """
    with open("db.json") as db:
        userData = json.load(db)
    """
    intial server config
    """
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 20000
    """
    Set argument value as the port number 
    """
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            SERVER_PORT = int(sys.argv[1])
    """
    20000 - current server ports are all other outgoing nodes 
    """
    outList = []
    if SERVER_PORT > 20000:
        for i in range(SERVER_PORT-20000):
            outList.append((SERVER_IP, 20000+i))
    """
    Initial the sever with the outgoing list
    """
    if len(outList) > 0:
        s = ServerThread(SERVER_IP, SERVER_PORT, outList)
    else:
        s = ServerThread(SERVER_IP, SERVER_PORT)
    serverInstance = s
    s.start()
    """
    Http port to the webpage clienta
    """
    httpPort = 8080 + SERVER_PORT - 20000
    print('# http port number ', httpPort)
    app.run(host='127.0.0.1', debug = True, port=httpPort, use_reloader=False)