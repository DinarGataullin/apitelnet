import socket
import sys
import logging
import psycopg2, psycopg2.extensions
from thread import *

logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG)

HOST = ''
PORT = 8000
FUNCSPUB = ['getrate', 'getvendors', 'getpublicproduct', 'getsellrate']
FUNCSPRIVATE = ['getbalance', 'getdailyusagebydestination', 'getgailyotalusage', 'getdailyusagebytrunk', 'getdailyusagebyvendor', 'gettrunklist', 'getroutingfortrunk', 'adddestinationtotrunk', 'removedestinatinofromtrunk', 'checkcdr']
DBPARAMS = {
    'dbname': 'icxp_v5',
    'user': 'postgres',
    'host': 'localhost'
}

try:
    pgcon = psycopg2.connect(**DBPARAMS)
    cur = pgcon.cursor(cursor_factory=psycopg2.extensions.cursor)
except:
    logging.error("DB connect error!")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    logging.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

s.listen(1000)


def parsetelnet(recived):
    recived = recived[:-2].split(' ')
    if recived[0].lower() in FUNCSPUB:
        return "Result for public function " + recived[0]
    elif recived[0].lower() in FUNCSPRIVATE:
        return "Result for private function " + recived[0]
    else:
        return "Function not exist"


def takeauthtoken(username, password):
    query = "SELECT * FROM apiservertable WHERE username="+username
    cur.execute(query)



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
    logging.info('Connected client: ' + addr[0] + ':' + str(addr[1]))
    start_new_thread(clientthread, (conn,))

s.close()