import socket
import sys
import sqlite3
from thread import *

HOST = ''
PORT = 8000
FUNCSPUB = ['getrate', 'getvendors', 'getpublicproduct', 'getsellrate']
FUNCSPRIVATE = ['getbalance', 'getdailyusagebydestination', 'getgailyotalusage', 'getdailyusagebytrunk', 'getdailyusagebyvendor', 'gettrunklist', 'getroutingfortrunk', 'adddestinationtotrunk', 'removedestinatinofromtrunk', 'checkcdr']

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

s.listen(1000)


def parsetelnet(recived):
    recived = recived[:-2].split(' ')
    if recived[0].lower() in FUNCSPUB:
        return "public: " + recived[0]
    elif recived[0].lower() in FUNCSPRIVATE:
        return "private: " + recived[0]
    else:
        return recived


def clientthread(conn):
    conn.send('Hello! Enter function name and parameters\r\nLike this: GetRate Vendor,Destionation\r\n')

    while True:

        buff = 1024
        data = ''
        while '\n' not in data:
            data += conn.recv(buff)
        res = parsetelnet(data)
        print res
        conn.sendall(''.join(res)+'\r\n')

    conn.close()

while 1:
    conn, addr = s.accept()
    print 'Connected client: ' + addr[0] + ':' + str(addr[1])
    start_new_thread(clientthread, (conn,))

s.close()