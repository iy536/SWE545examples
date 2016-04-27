#!/usr/bin/env python


import socket
s = socket.socket()
host = "127.0.0.1"
port = 12346
s.connect((host, port))
s.send("TIC")
print s.recv(1024)
s.close()
