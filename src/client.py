import json
import os
from select import select
import socket
import threading
from time import sleep
from machinalogger import createMachinaLogger
from preamble import Preamble

class Client:
    """
    A Client that will receive a file and its accompanying metadata
    in order to create a local copy from the remote source.

    Given in the spec, the client shall also deconstruct the stl file
    into a vertices csv file.
    """

    def __init__(self, fileName: str, host: str, port: str):
        self.outFileName = fileName
        self.netSockThread = threading.Thread(target=self.runNetSockImpl, args=(host, port), daemon=True)
        self.zmqThread = threading.Thread(target=self.runZMQImpl, args=(host, port), daemon=True)
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
            s.connect((host, int(port)))
            self.logger.info(f"Successfully connected to {host}:{port}")
            while (self.running):
                #python3 differentiates between bytes and string objects
                jsonBlob = s.recv(4096)
                #'cast' jsonBlob into ascii via decode method and then create json str
                jsonMap = json.loads(jsonBlob.decode('utf-8'))
                self.logger.debug(f"Preamble metadata received: {jsonMap}")
                
                #send an ACK equivalent to suggest to the server we are ready
                #for the main stl file
                s.send(jsonBlob)

                with open(self.outFileName, "wb") as outFile:
                    #now read the actual file
                    bufSize = 2**16
                    bytesRx = s.recv(bufSize)
                    while (bytesRx):
                        outFile.write(bytesRx)
                        bytesRx = s.recv(bufSize)
                #now verify cksum and filesize match the preamble data
                expectedPreamble = Preamble.from_json(jsonBlob.decode('utf-8'))
                currentPreamble = Preamble(self.outFileName)
                currentPreamble.generatePreamble()
                if not expectedPreamble == currentPreamble:
                    self.logger.error(f"Preamble and outfile metadata do not match! expected: {expectedPreamble} written: {currentPreamble}")
                else:
                    print("Done!")
                    self.logger.info(f"File successfully saved to {self.outFileName}")
                s.shutdown(socket.SHUT_RDWR)
                break

    def runZMQImpl(self, host: str, port: str):
        #run zeromq stuff?
        pass