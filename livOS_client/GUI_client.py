from nicegui import ui
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
            filedat=str(client_socket.recv(1024).decode())
            if not filedat.startswith("-2"):
                file_path = os.path.join(base_folder, filen)
                with open(file_path,"w") as file:
                    file.write(filedat)
                    file.close()
                print(f"file {filen} saved")

def downloader(client_socket):
    #client_socket.
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
    return client_socket.recv(1024).decode()





state = {'username': '', 'password': ''}
ui.input(label='Username', on_change=lambda e: state.update({'username': e.value}))
ui.input(label='Password', password=True, on_change=lambda e: state.update({'password': e.value}))
ui.button('Click me!', on_click=lambda: servret.set_text(login(client_socket,state['username'],state["password"])))
servret=ui.label()
ui.run()




