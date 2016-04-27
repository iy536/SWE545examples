import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue
import time

class ReadThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue, screenQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue

    def incoming_parser(self, data):
        data = data.strip()
        print "Server: " + data

        if data[0:3] == "TIC":
            data = data[3:]

        if len(data) == 0:
            return

        if len(data) > 3 and not data[3] == " ":
            response = "ERR"
            self.csoc.send(response)
            return
        rest = data[4:]

        if data[0:3] == "BYE":
            return 1

        if data[0:3] == "ERL":
            self.screenQueue.put("-Server- Nick not registered.")

        if data[0:3] == "HEL":
            self.nickname = rest
            self.screenQueue.put("-Server- Registered as <" + self.nickname + ">")

        if data[0:3] == "REJ":
            self.screenQueue.put("-Server- Nick exists. Forcing quit.")
            return 1

        if data[0:3] == "MNO":
            self.screenQueue.put("-Server- User not found.")

        if data[0:3] == "MSG":
            splitted = rest.split(":",1)
            self.screenQueue.put("*"+splitted[0]+"*: " + splitted[1])

        if data[0:3] == "SAY":
            splitted = rest.split(":",1)
            self.screenQueue.put("<"+splitted[0]+">: " + splitted[1])

        if data[0:3] == "SYS":
            self.screenQueue.put("-Server- " + rest)

        if data[0:3] == "LSA":
            splitted = rest.split(":")
            msg = "-Server- Registered nicks: "
            for i in splitted:
                msg += i + ","
            msg = msg[:-1]

            self.screenQueue.put(msg)

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            ret = self.incoming_parser(data)
            if ret == 1:
                time.sleep(1)
                self.csoc.close()
                # self.app.done(0)
                break

                # threadi bitirmeyi icap eden durun olursa donguden cik


class WriteThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.threadQueue = threadQueue

    def run(self):
        t = 0;
        while True:
            counter = 1
            while not counter == 100:
                counter += 1
                time.sleep(0.1)
                if self.threadQueue.qsize() > 0:
                    break

            if self.threadQueue.qsize() > 0:
                queue_message = str(self.threadQueue.get())
                print "Client: " + queue_message
                try:
                    self.csoc.send(queue_message)
                except socket.error:
                    self.csoc.close()
                    break
            else:
                try:
                    self.threadQueue.put("TIC")
                except socket.error:
                    self.csoc.close()
                    break


class ClientDialog(QDialog):
    ''' An example application for PyQt. Instantiate
        and call the run method to run. '''
    def __init__(self, threadQueue, screenQueue):

        self.threadQueue = threadQueue
        self.screenQueue = screenQueue

        # create a Qt application --- every PyQt app needs one
        self.qt_app = QApplication(sys.argv)

        # Call the parent constructor on the current object
        QDialog.__init__(self, None)

        # Set up the window
        self.setWindowTitle('IRC Client')
        self.setMinimumSize(500, 200)

        # Add a vertical layout
        self.vbox = QVBoxLayout()

        # The sender textbox
        self.sender = QLineEdit("", self)

        # The channel region
        self.channel = QTextBrowser()

        # The send button
        self.send_button = QPushButton('&Send')

        # Connect the Go button to its callback
        self.send_button.clicked.connect(self.outgoing_parser)

        # Add the controls to the vertical layout
        self.vbox.addWidget(self.channel)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)

        # start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateText)
        # update every 100 ms
        self.timer.start(10)


        # A very stretchy spacer to force the button to the bottom
        # self.vbox.addStretch(100)

        # Use the vertical layout for the current window
        self.setLayout(self.vbox)

    def updateText(self):
        if not self.screenQueue.empty():
            data = self.screenQueue.get()
            t = time.localtime()
            pt = "%02d:%02d" % (t.tm_hour, t.tm_min)
            self.channel.append(pt + " " + data)
        else:
            return

    def outgoing_parser(self):
        data = self.sender.text()
        self.screenQueue.put("-Local-: " + data)
        if len(data) == 0:
            return
        if data[0] == "/":
            rest = data[1:]
            splitted = rest.split(" ",3)
            command = splitted[0]

            if command == "list":
                self.threadQueue.put("LSQ")
                self.screenQueue.put("-Local-: Channel list requested.")

            elif command == "quit":
                self.threadQueue.put("QUI")
                self.screenQueue.put("-Local-: Leaving.")

            elif len(splitted) == 2:
                second = splitted[1]
                if command == "nick":
                    self.threadQueue.put("USR " + second)
                else:
                    self.screenQueue.put("-Local-: Command Error.")

            elif len(splitted) == 3:
                second = splitted[1]
                third = splitted[2]
                if command == "msg":
                    self.threadQueue.put("MSG " + second + ":" + third)
                else:
                    self.screenQueue.put("-Local-: Command Error.")

            else:
                self.screenQueue.put("-Local-: Command Error.")
        else:
            self.threadQueue.put("SAY " + data)

        self.sender.clear()

    def run(self):
        ''' Run the app and show the main form. '''
        self.show()
        self.qt_app.exec_()


# connect to the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#host = "10.1.1.10"
host = "127.0.0.1"
port = 12345
s.connect((host,port))

sendQueue = Queue.Queue()
screenQueue = Queue.Queue()

app = ClientDialog(sendQueue,screenQueue)

# start threads
rt = ReadThread("ReadThread", s, sendQueue, screenQueue)
rt.start()

wt = WriteThread("WriteThread", s, sendQueue)
wt.start()

app.run()

rt.join()
wt.join()
s.close()

