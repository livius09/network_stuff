import socket
import os
import time


#client_socket.sendall("".encode())
#client_socket.recv(1024).decode()

#os.chdir("livOS_client")

HOST = '127.0.0.1'
PORT = 12345

print("started client for livOS")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print("sucsesfully conected to the livOS server")


version = "client for livOS 1.1"


def download(client_socket):
    #client_socket.settimeout(2)
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
            client_socket.sendall("-1".encode())
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
                client_socket.sendall("-1".encode())
                break
            client_socket.sendall(filen.encode())

            filedat=[]
            filesize=0
            bytes_received=0

            tmp=str(client_socket.recv(1024).decode())

            if tmp.startswith("-2"):
                continue

            filesize=int(tmp.split(":")[1])

            print(f"filesize:{filesize}")
            client_socket.settimeout(2)

            while bytes_received < filesize:
                client_socket.settimeout(2)
                try:
                    data = client_socket.recv(min(1024, filesize - bytes_received))
                except:
                    break
                if not data:
                    break
                filedat.append(data)
                bytes_received += len(data)
                print(f"bytes recived:{bytes_received}")

            client_socket.settimeout(None)

            print("recived data")

            filedat=b"".join(filedat)
            

            file_path = os.path.join(base_folder, filen)
            with open(file_path,"wb") as file:
                file.write(filedat)
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
    time.sleep(0.1) #every wait is just cause some bs of it being to fast
    d=client_socket.recv(1024).decode()
    client_socket.sendall(user.encode())
    time.sleep(0.1)
    d=client_socket.recv(1024).decode()
    time.sleep(0.1)
    client_socket.sendall(pas.encode())
    time.sleep(0.1)
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
           download(client_socket)
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