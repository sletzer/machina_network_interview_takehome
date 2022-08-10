#!/usr/bin/env python3
import os
import argparse
import signal
from time import sleep

from machinalogger import createMachinaLogger
from server import Server
from client import Client

parser = argparse.ArgumentParser(description="A simple server/client program to demonstrate sending files using a variety of network libraries")
parser.add_argument("-s", "--server", help="Start the server process", action='store_true')
parser.add_argument("-c", "--client", help="Start the client process", action='store_true')
parser.add_argument("-f", "--filename", help="The file to be delivered to the client (if the server) or where to write the file that is being received (if the client)", required=True)
parser.add_argument("-H", "--host", help="The host IP address (to bind to for server, connect to for client)", required=True)
parser.add_argument("-p", "--port", help="port (for server to listen on, for client to connect to)", required=True)
parser.add_argument("--remotehost", help="The remote IP of the machine running in client mode", default="127.0.0.1")

args = parser.parse_args()

sigCaught = False

def sigHandler(signum, frame):
    global sigCaught
    sigCaught = True

def main() -> int:
    #setup signal handler to handle ctl+c from keyboard (or any other proc)
    signal.signal(signal.SIGINT, sigHandler)

    if args.server:
        netObj = Server(args.filename, args.host, args.port, args.remotehost)
    elif args.client:
        netObj = Client(args.filename, args.host, args.port)
    else:
        print("Must specify either client or server")
        return 255
    
    netObj.run()
    while not sigCaught and netObj.isRunning():
        sleep(0.5)
    netObj.stop()

if __name__ == "__main__":
    exitStatus = main()
    exit(exitStatus)
    