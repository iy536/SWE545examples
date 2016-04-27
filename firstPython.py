import xmlrpclib
import random

num1 = random.randint(0,100)
num2 = random.randint(0,100)

print (num1, num2)


server = xmlrpclib.Server("http://www.advogato.org/XMLRPC")
server.test.sumprod(num1, 7)


server.test.square(7)
server.test.strlen("Vildan")

