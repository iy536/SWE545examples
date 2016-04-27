#!/usr/bin/env python

import socket                   # Import socket module
s = socket.socket()             # Create a socket object
host = "127.0.0.1"          # Get local machine name
port = 12346                    # Reserve a port for your service.
s.connect((host, port))
print s.recv(1024)              # 1024 character lik buffer aliyor recv
# s.close()                       # Close the socket when done