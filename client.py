import threading
import socket

nickname=input("enter nickname:")
if nickname=="admin":
    password=input("enter password for admin:")

host="192.168.1.39"
port=9909
stop_thread=False
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((host,port))

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message=client.recv(1024).decode('ascii')    #receiveing message from server
            if message=="nick":
                client.send(nickname.encode('ascii'))
                next_message=client.recv(1024).decode('ascii')
                if next_message=="PASS":
                    client.send(password.encode("ascii"))
                    if client.recv(1024).decode('ascii')=='REFUSE':
                        print("connection was refused! wrong password")
                        stop_thread=True
                elif next_message=="BAN":
                    print("connection refused as banned")
                    client.close()
                    stop_thread=True
            else:
                print(message)          #if other than 'nick' word is sent by server then we simply print that message
        except:
            print("an error occurred")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break
        message=f'{nickname}: {input("")}'      #user has only 2 options|One is closing client|Another is writing new message to server
        if message[len(nickname)+2:].startswith('/'):    # username: /kick
            if nickname=='admin':
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('ascii'))
                elif message[len(nickname)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('ascii'))
            else:
                print("commands can only be used by admin")
        else:
            client.send(message.encode('ascii'))

receive_thread=threading.Thread(target=receive)
receive_thread.start()

write_thread=threading.Thread(target=write)
write_thread.start()
