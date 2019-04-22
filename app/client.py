import socket, time

class Client:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))


if __name__ == '__main__':
    client = Client()
    client.connect('127.0.0.1', 20000)
    msg = ''
    i = 0
    while True:
        msg = 'i = ' + str(i)
        client.sock.sendall(msg.encode())
        msg = client.sock.recv(8192)
        print(msg.decode())
        time.sleep(2)
        i += 1
