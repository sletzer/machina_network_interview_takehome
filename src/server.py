import os
from select import select
import socket
import threading
from unittest import runner
from machinalogger import createMachinaLogger
from preamble import Preamble
import zmq


class Server:
    """
    The Server class is a multithreaded network impl that serves a file
    to a given remote client

    see README.md for protocol details
    """    

    #default arguments
    HOST = socket.gethostbyname("localhost") 
    PORT = 0 #any port number, we don't care

    def __init__(self, fileName: str, host: str = HOST, port: str = PORT):
        self.txFileName = fileName
        self.netSockThread = threading.Thread(target=self.runNetSockImpl, args=(host, port), daemon=True)
        self.zmqThread = threading.Thread(target=self.runZMQImpl, args=(host, port), daemon=True)
        self.logger = createMachinaLogger("server.log")
    
    def run(self):
        self.running = True
        self.netSockThread.start()
        self.zmqThread.start()

    def stop(self):
        self.running = False

    def isRunning(self):
        return self.running == True

    def runNetSockImpl(self, host: str, port: str):
        #listen, bind, accept, pass preamble + actual file
        self.logger.info(f"About to create socket on {host} {port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #name to the socket with host + port
            s.bind((host, int(port)))
            #only allow for 1 connection to be queued, reject any others
            s.listen(1)
            while(self.running):
                conn, addr = s.accept()
                self.logger.debug(f"Accepted new connection from {addr}")
                #generate preamble
                preambleStr = str(Preamble(self.txFileName))
                #send preamble
                bytesTx = conn.send(preambleStr.encode('utf-8'))
                if bytesTx < len(preambleStr):
                    #short write
                    self.logger.error(f"Short write for preamble {bytesTx}/{len(preambleStr)}")
                    #break out of loop and with context, closing connection with client
                    break
                #wait for OK/ACK reply
                _ = conn.recv(4096)
                #now send the file down the wire
                with open(self.txFileName, "rb") as stlFile:
                    fileLen = os.path.getsize(self.txFileName)
                    #note: sendfile() reduces context switching by doing file read/writes 
                    #solely in kernel-space until file EOF encountered
                    bytesTX = conn.sendfile(stlFile)
                    if bytesTX < fileLen:
                        self.logger.error(
                            f"Could not send the whole file, only {bytesTX} out of {fileLen} sent")
                    else:
                        self.logger.debug(f"sent {self.txFileName} successfully to {addr}")
                        conn.close()
                    self.logger.debug(f"client {conn} has quit the connection")
                    print("Done! - TX")

    def runZMQImpl(self, host: str, port: str):
        ctx = zmq.Context()
        dealer = ctx.socket(zmq.DEALER)

        dealer.connect("tcp://" + host + ":" + "8091")
        self.logger.debug("ZeroMQ connected")

        #announce our existence
        dealer.send(b"fetch")

        #receive the preamble
        jsonBlob = dealer.recv()
        #jsonBlob = dealer.recv_multipart()
        expectedPreamble = Preamble.from_json(jsonBlob.decode('utf-8'))

        #ACK back
        dealer.send(jsonBlob)

        with open("/tmp/output_server.stl", "wb") as outFile:
            total = 0
            chunks = 0
            while(self.running):
                chunk = dealer.recv()
                chunks += 1
                size = len(chunk)
                total += size
                if size == 0:
                    #whole file is recieved
                    break
                bytesWritten = outFile.write(chunk)
                if bytesWritten < size:
                    self.logger.error(f"Short write on {outFile} only {bytesWritten}/{size}... aborting")
                    self.running = 0
                    ctx.term()
                    return
        
        currPreamble = Preamble("/tmp/output.stl")
        currPreamble.generatePreamble()

        if not currPreamble == expectedPreamble:
            self.logger.error("File download corrupted, aborting...")
            print("Failed")
        else:
            print("Done! - RX")
        self.running = False