import sys #Konsola arguman girmek icin

def parser(fileName):
    f = open("codes.txt","r")
    codes = {}
    for line in f:
        a = line.strip().split(" ",1)
        codes[a[1]] = int(a[0])
    return codes

myDict = parser("codes.txt")

try:
    a = sys.argv[1]
    ret = myDict[a]
    print a, ": ", ret

except KeyError:
    print "Country COde Not Found"

### Ya da alttaki satirlari deneyebiliriz
# #print myDict
# print myDict["Canada"]
# print myDict["Turkey"]
# print myDict[sys.argv[1]]

