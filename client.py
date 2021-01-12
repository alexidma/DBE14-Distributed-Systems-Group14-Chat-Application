# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 11:41:03 2021

@author: Yen Vy Huynh
"""

import socket
import threading
import os


# Buffer size
buffer_size = 1024

# Server list
servers=[]
clients_1=[]

def broadcast_s():
    # Create a UDP socket
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set the socket to broadcast and enable reusing addresses
    send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   
    # Broadcast address and port
    BROADCAST_IP = '192.168.1.255'
    BROADCAST_PORT = 5973
    
    # Local host information
    MY_HOST = socket.gethostname()
    MY_IP = socket.gethostbyname(MY_HOST)


    # Send broadcast message
    message = MY_IP + ':I want to join the chat.'
    
    # Send message on broadcast address
    send_socket.sendto(str.encode(message), (BROADCAST_IP, BROADCAST_PORT))
       
    print('Waiting for reply broadcast messages...\n')
    
    while True:
        data, addr = send_socket.recvfrom(buffer_size)
        print(data.decode(),'\n')
        
        if data:                      
            server2_addr = addr[0]
            return(server2_addr)

def broadcast_l():
    # Listening port
    BROADCAST_PORT = 5973

    # Local host information
    MY_HOST = socket.gethostname()
    MY_IP = socket.gethostbyname(MY_HOST)

     # Create a UDP socket
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set the socket to broadcast and enable reusing addresses
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind socket to address and port
    listen_socket.bind((MY_IP, BROADCAST_PORT))
    
    print('Listening to broadcast messages...')
    
    
    while True:
        data, addr = listen_socket.recvfrom(buffer_size)       
        recv_3 = (data.decode()).split(':')[1]
           
        #Split into Client and Server broadcast
        a = 'I want to join the chat.'
        b = 'I want to join the server_group.'

           #print(data.decode())
          
        if a == recv_3:
            client_addr = addr
            if client_addr not in clients_1:
                clients_1.append(client_addr)
                print('\nA Client has connected. Current client list: ',clients_1)
        if b == recv_3:
            server_addr = addr[0]
            if server_addr not in servers and server_addr!=MY_IP:
                servers.append(server_addr)
                print('\nA Server has connected. Server list:',servers)
  

shutdown = False

def receving(name, sock):
    while not shutdown:
        try:

            while True:
                data, address = client_socket.recvfrom(buffer_size)

                print ('>',data.decode())
        except:
            pass
        

    
"""
def heartbeat():
    from time import ctime, sleep
    import sys

    SERVERIP = '127.0.0.1'   # local host, just for testing
    HBPORT = 43278           # an arbitrary UDP port
    BEATWAIT = 10             # number of seconds between heartbeats
    
    if len(sys.argv)>1:
        SERVERIP=sys.argv[1]
    if len(sys.argv)>2:
        HBPORT=sys.argv[2]
    
    hbsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print ("PyHeartBeat client sending to IP %s , port %d"%(SERVERIP, HBPORT))
    #print ("\n*** Press Ctrl-C to terminate ***\n")
    while True:
        hbsocket.sendto(('Thump!').encode(), (SERVERIP, HBPORT))
        if __debug__:
            print ("Banane")
        sleep(BEATWAIT)
"""        
if __name__ == '__main__':
    try: 
       
        # Server application IP address and port
        server_address = broadcast_s()
        server_port = 10001
        server = (server_address, server_port)
       
        #start broadcast_listener
        t3=threading.Thread(target=broadcast_l)
        t3.start()
        
        # Create a UDP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Add username
        username = input('Please enter your username to join the chat: ')
        
        
        # Message sent to server
        client_socket.sendto(('Hi from ' + str(os.getpid()) + ' at ' + server_address + ':' + str(server_port) + '. My username is ' + username).encode(),(server_address, server_port))
        
        #t1=threading.Thread(target=heartbeat)
        #t1.start()
        
        # Receive response from server
        print('\nWaiting for response from server...\n')
        data, address = client_socket.recvfrom(buffer_size)
        print ('Server send a message: ', data.decode())
        
        print ('\nYou can start chatting now!\n')
        
        t2=threading.Thread(target=receving, args=('RecvThread',server))
        t2.start()
        
        message = input()
        while message != 'Quit':
            if message != '':
                client_socket.sendto((username + ': ' + message).encode(), server)
        
            message = input()
        
          
        
        shutdown = True
        client_socket.sendto((username + ':left the chat').encode(), server)
        client_socket.close()
        
        print ('You left the chat')

    except KeyboardInterrupt:
        shutdown = True
        client_socket.sendto((username + ':left the chat').encode(), server)
        client_socket.close()
        print('You left the chat')
        
    
      

