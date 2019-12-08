"""
serve.py

Instantiates a socket-adventure `Server` and serves it on a specified
port.

You should not need to make any changes in this file.
"""
import sys

from server import Server

try:
    PORT = int(sys.argv[1])
except IndexError:
    print("Please include a port number, eg: python serve.py 50000")
    exit(-1)

SERVER = Server(PORT)
SERVER.serve()
