import socket
import sys
import logging
import uuid
import hashlib
import time
import random
import string
import psycopg2
import psycopg2.extensions
from thread import *

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'logserver.log')
# api port and all interfaces
HOST = ''
PORT = 8881
# public functions
FUNCSPUB = ['getrate', 'getvendors', 'getpublicproduct', 'getsellrate']
# private functions
FUNCSPRIVATE = ['getbalance', 'getdailyusagebydestination', 'getgailyotalusage', 'getdailyusagebytrunk', 'getdailyusagebyvendor', 'gettrunklist', 'getroutingfortrunk', 'adddestinationtotrunk', 'removedestinatinofromtrunk', 'checkcdr']
# DB connect parameters
DBPARAMS = {
    'dbname': 'icxp_v5',
    'user': 'postgres',
    'host': 'localhost'
}

# connect to DB
def dbconnect(params):
    try:
        pgcon = psycopg2.connect(**params)
        cur = pgcon.cursor(cursor_factory=psycopg2.extensions.cursor)
        logging.info('Connected to Database succefully')
        return cur
    except:
        logging.error('DB connect error!')
        return None

# parse telnet input
def parse_telnet(recived, clientip):
    recived = recived[:-2]
    if recived.split(' ')[0] == 'adduser':
        if adduser(recived.split(' ')[1], recived.split(' ')[2]):
            return "User added!"
        else:
            return "Error user adding!"

    # check in first data is token
    if recived.split(':')[0]=='token':
        if recived.split(':')[1].split(' ')[0].lower() in FUNCSPRIVATE:
            return "It's PRIVATE function"
        else:
            return "Not private!"
    if recived.split(' ')[0] in FUNCSPUB:
        return "It's PUBLIC function"

def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

# take token for auth
def authtoken(username, password):
    cur = dbconnect(DBPARAMS)
    query = "SELECT * FROM apiserver WHERE username=\'{0}\'".format(username)
    cur.execute(query)
    row = cur.fetchone()
    if row:
        _, passhash, token, tokenexpiration = row
        if check_password(passhash, password):
            if token and float(tokenexpiration) > time.time():
                return token
            else:
                token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
                #token for 1 day
                tokenexpiration = time.time() + 24*60*60
                query = "UPDATE apiserver SET token=\'{0}\', tokenexpiration=\'{1}\' WHERE username=\'{2}\'".format(token, tokenexpiration, username)
                cur.execute(query)
                return token
        else:
            return "Username or password incorrect"
    else:
        return "Username or password incorrect"


def adduser(username, password):
    if username and password:
        cur = dbconnect(DBPARAMS)
        query = "insert into apiserver (username, password) values (\'{0}\',\'{1}\')".format(username, password)
        cur.execute(query)
        return True
    else:
        return False

def check_token(token):
    cur = dbconnect(DBPARAMS)
    query = "SELECT * FROM apiserver WHERE token=\'{0}\'".format(token)
    cur.execute(query)
    row = cur.fetchone()
    if row and float(row[3])>time.time():
        return True
    else:
        return False


def client_thread(conn, clientip):
    conn.send('Hello {0}! Enter function name and parameters\r\nLike this: GetRate Vendor,Destionation\r\n'.format(clientip))
    while True:
        buff = 1024
        data = ''
        while '\n' not in data:
            data += conn.recv(buff)
        res = parse_telnet(data, clientip)
        print res
        conn.sendall(''.join(res)+'\r\n')

    conn.close()


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((HOST, PORT))
        print 'Port opened!'
        logging.info('Port opened')
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        logging.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    s.listen(1000)

    while 1:
        conn, addr = s.accept()
        logging.info('Connected client: ' + addr[0] + ':' + str(addr[1]))
        # create new tread for each connection
        start_new_thread(client_thread, (conn, addr[0]))

    s.close()

if __name__ == "__main__":
    main()