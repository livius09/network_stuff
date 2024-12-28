#livOS
import socket
import hashlib

host= '127.0.0.1'
port=12345

with open("userf.txt", "r") as file:  # "r" is for read mode
    content = file.read()
    users=content.split(",")


with open("pswf.txt", "r") as file:  # "r" is for read mode
    content = file.read()
    paswords=content.split(",")


with open("authf.txt", "r") as file:  # "r" is for read mode
    content = file.read()
    auths=content.split(",")


curuser=None
curauth=None

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind((host,port))
serv.listen(5)

print(f"server is listening on {host}:{port}")


try:
    while True:  
        
        client_sok, client_adr = serv.accept()
        print(f"connection from {client_adr}")

        while True:
            dat = client_sok.recv(1024).decode().strip().lower()
            if not dat:
                print(f"Client {client_adr} disconnected.")
                break
            response="try help for a list of comands"

            print("dat:"+dat)
            if dat == "help":
                response =(
                "---------- \n"
                "This is a WIP goffi ah server \n" 
                "livOS\n" "---------- \n" 
                "comands: \n" "-Help \n"
                "-kill \n"
                "-echo \n"
                "-exe \n"
                "-login")

            elif dat == "kill":
                client_sok.sendall("Goodbey from livOS".encode())
                break

            elif dat == "echo":
                client_sok.sendall(client_sok.recv(1024))
                continue

            elif dat == "login":
                client_sok.sendall("Username: ".encode())
                username = client_sok.recv(1024).decode().strip()
                client_sok.sendall("Pasword: ".encode())
                pasword = client_sok.recv(1024).decode().strip()
                if username in users and hashlib.sha256(pasword.encode()).hexdigest()==paswords[users.index(username)]:
                    curuser=username
                    curauth=auths[users.index(curuser)]
                    response=f"login sucsesfull welcome {curuser} whit auth level {curauth} from ip: {client_adr}"
                else:
                    response="login faild wrong usser name or pasword"
                
            
            response=response+"\n"
            client_sok.sendall(response.encode())
     
except KeyboardInterrupt:
    print("\n Server shutting down.")
finally:
    client_sok.close()
    serv.close()
