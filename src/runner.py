#!/bin/env python3
import os
import argparse
import signal
from time import sleep

from machinalogger import createMachinaLogger
from server import Server

parser = argparse.ArgumentParser(description="A simple server/client program to demonstrate sending files using a variety of network libraries")
parser.add_argument("-s", "--server", help="Start the server process", action='store_true')
parser.add_argument("-c", "--client", help="Start the client process", action='store_true')
parser.add_argument("-f", "--filename", help="The file to be delivered to the client (if the server) or where to write the file that is being received (if the client)", required=True)

args = parser.parse_args()

sigCaught = False

def sigHandler(signum, frame):
    global sigCaught
    sigCaught = True

def main() -> int:
    #create logger
    logger = createMachinaLogger(__name__, "runner.log") 
    #setup signal handler
    signal.signal(signal.SIGQUIT, sigHandler)
    if args.server:
        server = Server(args.filename)
        server.run()
        while not sigCaught:
            sleep(0.5)
        server.stop()
    elif args.client:
        pass    
    else:
        print(f"Must specify either client or server")

if __name__ == "__main__":
    exitStatus = main()
    exit(exitStatus)
    