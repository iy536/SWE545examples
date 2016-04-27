
import sys #Konsola arguman girmek icin
import socket
import random

def parser(fileName):
    f = open("codes.txt","r")
    codes = {}
    for line in f:
        a = line.strip().split(" ",1)
        codes[a[1]] = int(a[0])
    return codes

myDict = parser("codes.txt")

s = socket.socket()          #create a socket object
# server = socket.gethostname()
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, server.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) | 1)

host = "0.0.0.0"
port = 12345
s.bind((host, port))
s.listen(5)

while True:
    c, addr = s.accept()
    print "Got Connection From", addr
##    N = len(myDict.keys())
##    i = random.randint(0,N)
##    countryName =  myDict.keys()[i]
##    countryCode =  myDict[countryName]
##    c.send("Country %s: Code: %d " % (countryName, countryCode))
##    c.close()
