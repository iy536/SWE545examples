#!/usr/bin/env python
import socket
import threading
import time
import Queue


class LoggerThread (threading.Thread):
    def __init__(self, name, logQueue, logFileName):
        threading.Thread.__init__(self)
        self.name = name
        self.lQueue = logQueue
        self.fid = open(logFileName, "a")

    def log(self,message):
        # gelen mesaji zamanla beraber bastir
        print(time.ctime() + ": " + message)
        self.fid.write(time.ctime() + ": " + message + "\n")
        self.fid.flush()

    def run(self):
        self.log("Starting " + self.name)
        while True:
            to_be_logged = self.lQueue.get()
            # self.fid.write("hede")
            self.log(to_be_logged)

        self.log("Exiting" + self.name)
        self.fid.close()


class WriteThread (threading.Thread):
    def __init__(self, name, csoc, address, logQueue, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.address = address
        self.threadQueue = threadQueue
        self.lQueue = logQueue

    def run(self):
        self.lQueue.put("Starting " + self.name)

        t = 0;

        while True:
            counter = 1
            while not counter == 100:
                counter += 1
                time.sleep(0.1)
                if self.threadQueue.qsize() > 0:
                    break

            try:
                self.csoc.send("TIC")
            except socket.error:
                self.lQueue.put("Socket problem in " + self.name)
                self.lQueue.put("Closing socket " + str(self.address))

                self.csoc.close()
                break

            if self.threadQueue.qsize() > 0:
                queue_message = self.threadQueue.get()
                if queue_message[0] and queue_message[1]:
                    message_to_send = "MSG " + queue_message[1] + ":" + queue_message[2]
                elif queue_message[1]:
                    message_to_send = "SAY " + queue_message[1] + ":" + queue_message[2]
                else:
                    message_to_send = "SYS " + queue_message[2]

                try:
                    self.csoc.send(message_to_send)
                except socket.error:
                    self.lQueue.put("Socket problem in " + self.name)
                    self.lQueue.put("Closing socket " + str(self.address))

                    self.csoc.close()
                    break
        self.lQueue.put("Exiting " + self.name)



class ReadThread (threading.Thread):
    def __init__(self, name, csoc, address, logQueue, threadQueue, fihrist):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.address = address
        self.nickname = ""
        self.threadQueue = threadQueue
        self.fihrist = fihrist
        self.lQueue = logQueue

    def parser(self, data):
        data = data.strip()

        if not self.nickname and not data[0:3] == "USR" and not data[0:3] == "TIC":
            response = "ERL "
            self.csend(response)
            return 0

        if len(data) > 3 and not data[3] == " ":
            response = "ERR"
            self.csend(response)
            return 0

        if data[0:3] == "USR":
            nickname = data[4:]
            if nickname not in self.fihrist.keys():
                # kullanici yoksa
                response = "HEL " + nickname
                self.csend(response)
                self.nickname = nickname
                self.fihrist.update({self.nickname:self.threadQueue})

                self.system_msg(("", "", self.nickname + " has joined."))
                self.lQueue.put(self.nickname + " has joined.")
                return 0

            else:
                # kullanici reddedilecekse
                response = "REJ " + nickname
                self.csend(response)
                # baglantiyi kapat
                self.csoc.close()
                return 1

        elif data[0:3] == "QUI":
            response = "BYE " + self.nickname
            self.csend(response)
            self.fihrist.pop(self.nickname)

            self.system_msg(("", "", self.nickname + " has left."))
            self.lQueue.put(self.nickname + " has left.")

            self.csoc.close()
            return 1

        elif data[0:3] == "LSQ":
            response = "LSA "
            for users in self.fihrist.keys():
                response += users + ":"
            self.csend(response[0:-1])
            return 0

        elif data[0:3] == "TIC":
            response = "TOC"
            self.csend(response)
            return 0

        elif data[0:3] == "SAY":
            message = data[4:]
            queue_message = ("", self.nickname, message)
            for q in fihrist.values():
                q.put(queue_message)
            response = "SOK"
            self.csend(response)
            return 0

        elif data[0:3] == "MSG":
            rest = data[4:]
            splitted = rest.split(":",1)
            to_nickname = splitted[0]
            message = splitted[1]
            if not to_nickname in self.fihrist.keys():
                response = "MNO"
            else:
                queue_message = (to_nickname, self.nickname, message)
                self.fihrist[to_nickname].put(queue_message)
                response = "MOK"
            self.csend(response)

        else:
            # bir seye uymadiysa protokol hatasi verilecek
            response = "ERR"
            self.csend(response)
            return 0

    def system_msg(self, message):
         for q in self.fihrist.values():
             q.put(message)

    def csend(self,ret):
        try:
            self.csoc.send(ret)
        except socket.error:
            self.lQueue.put("Socket problem in " + self.name)
            self.lQueue.put("Closing socket " + str(self.address))
            if self.nickname:
                self.fihrist.pop(self.nickname)
            self.csoc.close()

    def run(self):
        self.lQueue.put("Starting " + self.name)
        while True:
            try:
                data = self.csoc.recv(1024)
                print(data + "\n")
            except socket.error:
                self.system_msg(("","", self.nickname + " had a connection problem."))
                self.lQueue.put(self.nickname +  " had a connection problem.")
                try:
                    self.fihrist.pop(self.nickname)
                except:
                    pass
                self.csoc.close()

                break

            # threadi bitirmeyi icap eden durum olursa donguden cik
            a = self.parser(data)
            if a == 1:
                break

        self.lQueue.put("Exiting " + self.name)


logFile = "irc_server.log"
s = socket.socket()
# Create a socket object
host = "0.0.0.0"
# Get local machine name
port = 12345
# Reserve a port for your service.
s.bind((host, port))
# Bind to the port
s.listen(5)
# Now wait for client connection.

thread_counter = 0

# create fihrist
fihrist = dict()

logQueue = Queue.Queue()
lthread = LoggerThread("LoggerThread", logQueue, logFile)
lthread.start()

while True:
    print("Waiting for connection")
    logQueue.put("Waiting for connection")
    thread_counter += 1
    c, a = s.accept()
    # Establish connection with client.
    logQueue.put('Got connection from '+ str(a))
    threadQueue = Queue.Queue()
    newReadThread = ReadThread("ReadThread-" + str(thread_counter), c, a, logQueue, threadQueue, fihrist)
    newWriteThread = WriteThread("WriteThread-" + str(thread_counter), c, a, logQueue, threadQueue)
    newReadThread.start()
    newWriteThread.start()

lthread.join()
print("Main Thread exiting.")

