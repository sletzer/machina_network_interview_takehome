import json
import os
from select import select
import socket
import threading
from time import sleep
from machinalogger import createMachinaLogger
from preamble import Preamble

class Client:
    def __init__(self, fileName: str, host: str, port: str):
        self.outFileName = fileName
        self.netSockThread = threading.Thread(target=self.runNetSockImpl, args=(host, port))
        self.zmqThread = threading.Thread(target=self.runZMQImpl, args=(host, port))
        self.logger = createMachinaLogger("client.log")
    
    def run(self):
        self.running = True
        self.netSockThread.start()
        self.zmqThread.start()

    def stop(self):
        self.running = False

    def runNetSockImpl(self, host: str, port: str):
        #listen, bind, accept, pass preamble + actual file
        self.logger.info(f"About to create socket")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #set non blocking, so we can quit if need be
            s.setblocking(False)
            while (s.connect_ex((host, int(port))) and self.running):
                sleep(0.5)
            while (self.running):
                readIO, writeIO, _ = select([s], [s], [], 1.0)

                if len(readIO) > 0:
                    print("readIO is rdy")
                    jsonBlob = s.recv(4096)
                    jsonStr = json.loads(jsonBlob.decode('utf-8'))
                    print(jsonStr)
                    
                    #send an ACK equivalent to suggest to the server we are ready
                    s.send(jsonBlob)

                    with open(self.outFileName, "wb") as outFile:
                        #now read the actual file
                        bufSize = 2**16
                        bytesRx = s.recv(bufSize)
                        while (bytesRx > 0):
                            outFile.write(bytesRx)
                            bytesRx = s.recv(bufSize)
                if len(writeIO) > 0:
                    print("writeIO is ready")
                sleep(1)

    def runZMQImpl(self, host: str, port: str):
        #run zeromq stuff?
        pass