import socket
import sys
from thread import *

HOST = ''
PORT = 8000
FUNCSPUB = ['getrate', 'getvendors', 'getpublicproduct', 'getsellrate']
FUNCSPRIVATE = ['getbalance', 'getdailyusagebydestination', 'getgailyotalusage', 'getdailyusagebytrunk', 'getdailyusagebyvendor', 'gettrunklist', 'getroutingfortrunk', 'adddestinationtotrunk', 'removedestinatinofromtrunk', 'checkcdr']

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

s.listen(1000)
print 'Socket now listening'

def parsetelnet(recived):
    recived = recived.split(' ')
    if recived[0].lower() in FUNCSPUB:
        return "public"
    elif recived[0].lower() in FUNCSPRIVATE:
        return "private"
    else:
        return recived

def clientthread(conn):
    conn.send('Welcome to the server. Type something and hit enter\n')

    while True:

        buff = 1024
        data = ''
        while '\n' not in data:
            data += conn.recv(buff)
        res = parsetelnet(data)
        print res
        #conn.sendall(data)

    conn.close()


# now keep talking with the client
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread, (conn,))

s.close()