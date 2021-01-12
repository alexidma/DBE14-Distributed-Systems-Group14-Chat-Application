import socket
#import os
import time
import threading

#Buffer size
buffer_size = 1024

#Lists
clients = []
clients_1 = []
servers = []
message_list =[]

class Server(threading.Thread):
    def __init__(self, server_socket, received_data, client_address):
        super(Server, self).__init__()
        self.server_socket = server_socket
        self.received_data = received_data
        self.client_address = client_address

    # Override run method
    def run(self):
        # Message to be sent to client
        message = 'Hi ' + self.client_address[0] + ':' + str(self.client_address[1]) + '. This is server ' + MY_IP
        # Send message to client
        self.server_socket.sendto(str.encode(message), self.client_address)     

def client_handler():
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Server application IP address and port
    server_address = socket.gethostbyname(socket.gethostname())
    server_port = 10001
    
    # Bind socket to address and port
    server_socket.bind((server_address, server_port))
    print('Server up and running at {}:{} \n'.format(server_address, server_port))

    while True:
        try:
            # Receive message from client
            data, address = server_socket.recvfrom(buffer_size)
            recv_1 = (data.decode()).split(':')[0]
            recv_2 = (data.decode()).split(':')[1]
            recv_3 = (data.decode()).split('>>')[0]
            
            print('\n'+time.ctime(time.time()) + '> ' + str(recv_1) + ': ' + str(recv_2))
           
            c = 'left the chat' 
            d = 'A Server already existing. My IP is'
            
            message1 = str(recv_1) + ": " + str(recv_2)
            message2 = 'S>>'+str(recv_1) + ": " + str(recv_2)
            message_list.append(message1)
            
            
            if address not in clients and recv_1!=d and recv_3!='S':
                clients.append(address)  
                print('Client list: ',clients)
                t = Server(server_socket, data, address)
                t.start()
                t.join()
            elif address not in servers and recv_1==d:
                servers.append(address[0])
                print('Server list: ',servers)
            else:
                pass
            
            if c == recv_2:
                clients.remove(address)
                print(clients)
                
            # tried this for broadcasting to other clients  
            for client in clients:
                if client!=address:
                    server_socket.sendto(message1.encode(), client)
                    for server in servers:
                        server_socket.sendto(message2.encode(),(server,10001))
                elif client == address:
                    for server in servers:
                        server_socket.sendto(message2.encode(),(server,10001))

        except:
            pass  
    
def broadcast():
   # Create a UDP socket
   listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   
   # Set the socket to broadcast and enable reusing addresses
   listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
   listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   
   # Bind socket to address and port
   listen_socket.bind((MY_IP, BROADCAST_PORT))
   
   print('\nListening to broadcast messages')

   while True:
      
           data, addr = listen_socket.recvfrom(buffer_size)
           recv_3 = (data.decode()).split(':')[1]
           
           #Split into Client and Server broadcast
           a = 'I want to join the chat.'
           b = 'I want to join the server_group.'
          
           if a == recv_3:
               client_addr = addr
               if client_addr not in clients_1:
                   message = MY_IP + ' send you a broadcast message'
                   # Send message on broadcast address
                   listen_socket.sendto(str.encode(message), (client_addr))
                   clients_1.append(client_addr)
                   print('\nA Client has connected. Current broadcast client list: ',clients_1)
           if b == recv_3:
               server_addr = addr[0]
               if server_addr not in servers and server_addr!=MY_IP:
                   servers.append(server_addr)
                   print('\nA Server has connected. Server list:',servers)
                   listen_socket.sendto(str.encode('A Server already existing. My IP is: '+MY_IP), (server_addr,10001))         
   
def broadcast_s():   
    # Create a UDP socket
    sendserver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Set the socket to broadcast and enable reusing addresses
    sendserver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sendserver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Send broadcast message
    message = MY_IP + ':I want to join the server_group.'
    
    # Send message on broadcast address
    sendserver_socket.sendto(str.encode(message), (BROADCAST_IP, BROADCAST_PORT))
    
    sendserver_socket.close()

"""
HBPORT = 43278
CHECKWAIT = 20

from socket import AF_INET, SOCK_DGRAM
from threading import Lock, Thread, Event
from time import time, ctime, sleep
import sys

class BeatDict:
    "Manage heartbeat dictionary"

    def __init__(self):
        self.beatDict = {}
        if __debug__:
            self.beatDict['127.0.0.1'] = time()
        self.dictLock = Lock()

    def __repr__(self):
        list = []
        self.dictLock.acquire()
        for key in self.beatDict.keys(  ):
            list = "%sIP address: %s - Last time: %s\n" % (
                list, key, ctime(self.beatDict[key]))
        self.dictLock.release()
        return list

    def update(self, entry):
        "Create or update a dictionary entry"
        self.dictLock.acquire()
        self.beatDict[entry] = time()
        self.dictLock.release()

    def extractSilent(self, howPast):
        "Returns a list of entries older than howPast"
        silent = []
        when = time() - howPast
        self.dictLock.acquire(  )
        for key in self.beatDict.keys():
            if self.beatDict[key] < when:
                silent.append(key)
        self.dictLock.release()
        return silent

class BeatRec(Thread):
    "Receive UDP packets, log them in heartbeat dictionary"

    def __init__(self, goOnEvent, updateDictFunc, port):
        Thread.__init__(self)
        self.goOnEvent = goOnEvent
        self.updateDictFunc = updateDictFunc
        self.port = port
        self.recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recSocket.bind(('', port))

    def __repr__(self):
        return "Heartbeat Server on port: %d\n" % self.port

    def run(self):
        while self.goOnEvent.isSet(  ):
            if __debug__:
                print ("Waiting to receive...")
            data, addr = self.recSocket.recvfrom(buffer_size)
            if __debug__:
                print ("Received packet from ",addr)
            self.updateDictFunc(addr[0])

def main():
    "Listen to the heartbeats and detect inactive clients"
    global HBPORT, CHECKWAIT
    if len(sys.argv)>1:
        HBPORT=sys.argv[1]
    if len(sys.argv)>2:
        CHECKWAIT=sys.argv[2]

    beatRecGoOnEvent = Event(  )
    beatRecGoOnEvent.set(  )
    beatDictObject = BeatDict(  )
    beatRecThread = BeatRec(beatRecGoOnEvent, beatDictObject.update, HBPORT)
    if __debug__:
        print (beatRecThread)
    beatRecThread.start(  )
    print ("PyHeartBeat server listening on port %d" % HBPORT)
    print ("\n*** Press Ctrl-C to stop ***\n")
    while 1:
        try:
            if __debug__:
                print ("Beat Dictionary")
                print (beatDictObject)
            silent = beatDictObject.extractSilent(CHECKWAIT)
            if silent:
                print ("Silent clients")
                print (silent)
            sleep(CHECKWAIT)
        except KeyboardInterrupt:
            print ("Exiting.")
            beatRecGoOnEvent.clear()
            beatRecThread.join()
"""

if __name__ == '__main__':
    
    # Broadcast address and port
    BROADCAST_PORT = 5973
    BROADCAST_IP = '192.168.1.255'
    
    # Local host information
    MY_HOST = socket.gethostname()
    MY_IP = socket.gethostbyname(MY_HOST)
    
     
    # Start processes
    t3= threading.Thread(target=client_handler)
    t3.start()
    
    t1=threading.Thread(target=broadcast_s)
    t1.start()
    
    t2=threading.Thread(target=broadcast)
    t2.start()
    
    #t4=threading.Thread(target=main)
    #t4.start()
    
    t1.join()
    t2.join()      
    t3.join()
    #t4.join()

