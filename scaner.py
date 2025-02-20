import socket
import os

#client_socket.sendall("".encode())
#client_socket.recv(1024).decode()

target=socket.gethostbyname("google.com")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)




def ping(targ:str)->bool:
    response =os.system(f"ping -c 1 {targ} > /dev/null")
    if response == 0:
        return True
    
print(ping(target))

def port(targ:str,port,client_socket):
    client_socket.settimeout(1)
    try:
        client_socket.connect((targ, port))
        client_socket.close()
        return True
    except:
        return False

print(port(target,443,client_socket))
    