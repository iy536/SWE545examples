import socket
import time

def socketParser(csocket, data, codelist):
    data = data.strip()
    if len(data) < 3:
        response = "ERR"
        csocket.send(response)
        return 0
    if data[0:3] == "HEL":
        csocket.send("SLT")

    elif data[0:3] == "QUI":
        response = "BYE"
        csocket.send(response)
        csocket.close()
    elif data[0:3] == "GET":
        country = data[4:]
        # keys arasinda ulke var mi kontrol et
        if country in codelist.keys():
            response = "CDE %s" % (codelist[country])
            # cevap gonder
            csocket.send(response)
        else:
            response = "NTF %s" % country
            # hatali cevap gondere
            csocket.send(response)
    elif data[0:3] == "TIC":
        response = "TOC", time.ctime()
        csocket.send(response)
    else:
        response = "ERR"
        csocket.send(response)

def fileParser(fileName):
    f = open(fileName, 'r')
    codes = {}
    for line in f:
        a = line.strip().split(" ",1)
        codes[a[1]] = int(a[0])
    return codes

myDict = fileParser("codes.txt")
s = socket.socket()          #create a socket object
host = "0.0.0.0"
port = 12345
s.bind((host,port))
s.listen(5)

while True:
    c, addr = s.accept()
    print "Got connection from", addr

    while c:
        data = c.recv(1024)
        socketParser(c, data, myDict)