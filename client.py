""" The client code """
import socket
import sys

try:
    PORT = int(sys.argv[1])
except IndexError:
    print("Please include a port number, eg: python serve.py 50000")
    exit(-1)

CLIENT_SOCKET = socket.socket()
CLIENT_SOCKET.connect(("127.0.0.1", PORT))

while True:
    try:
        RESPONSE = CLIENT_SOCKET.recv(4096).decode()
    except ConnectionAbortedError:
        print("Connection closed by host.")
        break

    print(RESPONSE)
    if "Goodbye!" in RESPONSE:
        CLIENT_SOCKET.close()
        break
    else:
        MY_MESSAGE = input("> ").encode('utf-8') + b'\n'
        CLIENT_SOCKET.sendall(MY_MESSAGE)
