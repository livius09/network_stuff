import socket
import os

#client_socket.sendall("".encode())
#client_socket.recv(1024).decode()

HOST = '127.0.0.1'
PORT = 12345

print("started client for livOS")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print("sucsesfully conected to the livOS server")


version = "client for livOS 1.1"


def download(client_socket):
    base_folder = os.path.abspath("Downloads")
    client_socket.sendall("files".encode())
    while True:
        first=str(client_socket.recv(1024).decode())
        if first.startswith("-1"):
            break
        print(first)
        print(client_socket.recv(1024).decode())
        foldern=input("path:")
        if foldern=="-1":
            print("leaving folder view")
            break
        client_socket.sendall(foldern.encode())
        while True:
            third=client_socket.recv(1024).decode()
            if third.startswith("-2"):
                break
            print(third)
            print(client_socket.recv(1024).decode())
            filen=input("file to save:")
            if filen=="-1":
                break
            client_socket.sendall(filen.encode())
            filedat=str(client_socket.recv(1024).decode())
            if not filedat.startswith("-2"):
                file_path = os.path.join(base_folder, filen)
                with open(file_path,"w") as file:
                    file.write(filedat)
                    file.close()
                print(f"file {filen} saved")

def downloader(client_socket):
    base_folder = os.path.abspath("Downloads")
    client_socket.sendall("files".encode())
    print(client_socket.recv(1024).decode())
    print(client_socket.recv(1024).decode())
    foldern=input("path:")
    client_socket.sendall(foldern.encode())
    print(client_socket.recv(1024).decode())
    print(client_socket.recv(1024).decode())
    filen=input("file to save:")
    if filen=="-1":
        return
    client_socket.sendall(filen.encode())
    filedat=str(client_socket.recv(1024).decode())
    if not filedat.startswith("-2"):
        file_path = os.path.join(base_folder, filen)
        with open(file_path,"w") as file:
            file.write(filedat)
            file.close()
        print(f"file {filen} saved")
    client_socket.sendall("-1".encode())
    client_socket.recv(1024).decode()
    client_socket.recv(1024).decode()
    client_socket.sendall("-1".encode())
    client_socket.recv(1024).decode()

            

            

def login(client_socket,user,pas):
    client_socket.sendall("login".encode())
    d=client_socket.recv(1024).decode()
    client_socket.sendall(user.encode())
    d=client_socket.recv(1024).decode()
    client_socket.sendall(pas.encode())
    print(client_socket.recv(1024).decode())



try:
    while True:
        
        
        ein=input("$").lower()

        if ein=="help":
            print(f"{version}: \n"
              "login: login on the server whith your creds\n"
              "dowload: pull a file from the server into the clients download dir"
              "exit: close and exit the client"
              )
            
        elif ein == "download":
           downloader(client_socket)
        elif ein == "login":
            login(client_socket,input("username:"),input("pasword:"))
        elif ein == "exit":
           client_socket.close()
           exit()
        elif ein == 5:
            pass
        elif ein==7:
            pass
        elif ein==8:
            pass
        elif ein==9:
            pass
        else:
            print(f"{version} help for a list of comands")
    
            
finally:
    client_socket.close()