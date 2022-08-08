import os
from re import S
from select import select
import socket
import threading
from machinalogger import createMachinaLogger


class Server:
    HOST = socket.gethostbyname("localhost") 
    PORT = 0 #any port number, we don't care

    def __init__(self, fileName: str):
        self.txFileName = fileName
        self.netSockThread = threading.Thread(target=self.runNetSockImpl, args=(Server.HOST, Server.PORT))
        self.zmqThread = threading.Thread(target=self.runZMQImpl, args=(Server.HOST, Server.PORT))
        self.logger = createMachinaLogger(__name__, "server.log")
    
    def run(self):
        self.running = True
        self.netSockThread.start()
        self.zmqThread.start()

    def stop(self):
        self.running = False

    def runNetSockImpl(self, host: str, port: str):
        #listen, bind, accept, pass preamble + actual file
        self.logger.info(f"About to create socket on {host} {port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #set non blocking, so we can quit if need be
            s.setblocking(False)
            #name to the socket with host + port
            s.bind((host, port))
            #only allow for 1 connection
            s.listen(1)
            while(self.running):
                readIO, _, _ = select([s], [], [], timeout=1.0)
                #readIO list should only ever contain 1 elem and it should be s
                #if it is == s then we know select did not timeout and we have a connection
                #ready to be made
                if len(readIO) > 0:
                    conn, addr = s.accept()
                    self.logger.debug(f"Accepted new connection from {addr}")
                    with open(self.txFileName, "r") as stlFile:
                        fileLen = os.path.getsize(self.txFileName)
                        bytesTX = os.sendfile(conn.fileno(), stlFile.fileno(), None, fileLen)
                        if bytesTX < fileLen:
                            self.logger.error(
                                f"Could not send the whole file, only {bytesTX} out of {fileLen} sent")
                        else:
                            self.logger.debug(f"sent {self.txFileName} successfully to {addr}")
                    self.logger.debug(f"client {conn} has quit the connection")

    def runZMQImpl(self, host: str, port: str):
        #run zeromq stuff?
        pass