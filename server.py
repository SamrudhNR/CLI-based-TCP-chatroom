import threading
import socket
host="192.168.1.39"
port=9909

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

clients=[]
nicknames=[]

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            if msg.decode('ascii').startswith("KICK"):
                if nicknames[clients.index(client)]=='admin':  # if allowing kick or ban is only happening on client side then its bad.Because any user can manipulate client
                     name_to_kick=msg.decode('ascii')[5:]      # Only server should handle the permissions to kick or ban.SO when kick or ban command is sent to server
                     kick_user(name_to_kick)                   # we check if the nickname is admin. For this reason we used "if nicknames[clients.index[client]]=='admin'
                else:
                    client.send('command was refused'.encode('ascii'))
            elif msg.decode('ascii').startswith("BAN"):
                if nicknames[clients.index(client)]=='admin':
                    name_to_ban=msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt','a') as f:
                          f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned')
                else:
                    client.send('command was refused'.encode('ascii'))
            else:
                broadcast(message)
        except:
            if client in clients:
                index=clients.index(client)
                clients.remove(client)
                client.close()
                nickname=nicknames[index]
                broadcast(f'{nickname} left the chat'.encode('ascii'))
                nicknames.remove(nickname)
                break

def receive():
    while True:
        client,address=server.accept()
        print(f'connected with {str(address)}')
        client.send("nick".encode("ascii"))
        nickname=client.recv(1024).decode('ascii')

        with open('bans.txt','r') as f:
            bans=f.readlines()
        if nickname+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if nickname=='admin':
            client.send('PASS'.encode('ascii'))
            password=client.recv(1024).decode('ascii')

            if password!='adminpasss':                 #if password is wrong then send refuse message to client and close the client
                client.send("REFUSE".encode('ascii'))   # "continue" is used because if we use "break" then we will come out of while loop
                client.close()                          # so no further client is accepted. so by using "continue" we will continue accepting new clients
                continue                                # but refused client is not append to clients list

        nicknames.append(nickname)
        clients.append((client))

        print(f'nickname of client is {nickname}')
        broadcast(f'{nickname} joined d chat'.encode('ascii'))
        client.send(f'connected to server'.encode('ascii'))

        thread=threading.Thread(target=handle,args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index=nicknames.index(name)
        client_to_kick=clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("u were kicked by admin".encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by admin'.encode('ascii'))

print("server is listening...")
receive()

