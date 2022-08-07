import os
from re import S
import socket
import threading


class Server:
    HOST = socket.gethostbyname("localhost") 
    PORT = 0 #any port number, we don't care

    def Server(self, fileName: str):
        self.netSockThread = threading.Thread(target=self.runNetSockImpl, args=(Server.HOST, Server.PORT))
        self.zmqThread = threading.Thread(target=self.runZMQImpl, args=(Server.HOST, Server.PORT))
    
    def run(self):
        self.netSockThread.start()
        self.zmqThread.start()

    def runNetSockImpl(self, host: str, port: str):
        #listen, bind, accept, pass preamble + actual file
        pass

    def runZMQImpl(self, host: str, port: str):
        #run zeromq stuff?
        pass