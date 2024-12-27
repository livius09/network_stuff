#livOS
import socket
import hashlib

host= '127.0.0.1'
port=12345

user=["levi","ligma"]
psw= [hashlib.sha256("balls".encode()),hashlib.sha256("balls".encode())]

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
            if dat == "Help":
                response =(
                "---------- \n"
                "This is a WIP goffi ah server \n" 
                "livOS\n" "---------- \n" 
                "comands: \n" "-Help \n"
                "-kill \n"
                "-echo \n"
                "-exe")

            elif dat == "kill":
                client_sok.sendall("Goodbey from livOS".encode())
                break

            elif dat == "echo":
                client_sok.sendall(client_sok.recv(1024))
                continue

            elif dat == "exe":
                client_sok.sendall("your comands here: \n".encode())
                dat = client_sok.recv(1024).decode().strip().lower()
                exec(dat)
                continue
            
            response=response+"\n"
            client_sok.sendall(response.encode())
     
except KeyboardInterrupt:
    print("\n Server shutting down.")
finally:
    client_sok.close()
    serv.close()
